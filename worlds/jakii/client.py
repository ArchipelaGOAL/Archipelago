# Python standard libraries
import asyncio
import json
import logging
import os
import subprocess
import sys

from asyncio import Task
from datetime import datetime
from logging import Logger
from typing import Awaitable

# Misc imports
import colorama
import pymem

from pymem.exception import ProcessNotFound

# Archipelago imports
import ModuleUpdate
import Utils

from CommonClient import ClientCommandProcessor, CommonContext, server_loop, gui_enabled
from NetUtils import ClientStatus

# Jak imports
from .game_id import jak2_name
from .agents.memory_reader import Jak2MemoryReader
from .agents.repl_client import Jak2ReplClient
from . import JakIIWorld


ModuleUpdate.update()
logger = logging.getLogger("Jak2Client")
all_tasks: set[Task] = set()


def create_task_log_exception(awaitable: Awaitable) -> asyncio.Task:
    async def _log_exception(a):
        try:
            return await a
        except Exception as e:
            logger.exception(e)
        finally:
            all_tasks.remove(task)
    task = asyncio.create_task(_log_exception(awaitable))
    all_tasks.add(task)
    return task


class Jak2ClientCommandProcessor(ClientCommandProcessor):
    ctx: "Jak2Context"

    # The command processor is not async so long-running operations like the /repl connect command
    # (which takes 10-15 seconds to compile the game) have to be requested with user-initiated flags.
    # The flags are checked by the agents every main_tick.
    def _cmd_repl(self, *arguments: str):
        """Sends a command to the OpenGOAL REPL. Arguments:
        - connect : connect the client to the REPL (goalc).
        - status : check internal status of the REPL."""
        if arguments:
            if arguments[0] == "connect":
                self.ctx.on_log_info(logger, "This may take a bit... Wait for the success audio cue before continuing!")
                self.ctx.repl.initiated_connect = True
            if arguments[0] == "status":
                create_task_log_exception(self.ctx.repl.print_status())

    def _cmd_memr(self, *arguments: str):
        """Sends a command to the Memory Reader. Arguments:
        - connect : connect the memory reader to the game process (gk).
        - status : check the internal status of the Memory Reader."""
        if arguments:
            if arguments[0] == "connect":
                self.ctx.memr.initiated_connect = True
            if arguments[0] == "status":
                create_task_log_exception(self.ctx.memr.print_status())


class Jak2Context(CommonContext):
    game = jak2_name
    items_handling = 0b111  # Full item handling
    command_processor = Jak2ClientCommandProcessor

    # We'll need two agents working in tandem to handle two-way communication with the game.
    # The REPL Client will handle the server->game direction by issuing commands directly to the running game.
    # But the REPL cannot send information back to us, it only ingests information we send it.
    # Luckily OpenGOAL sets up memory addresses to write to, that AutoSplit can read from, for speedrunning.
    # We'll piggyback off this system with a Memory Reader, and that will handle the game->server direction.
    repl: Jak2ReplClient
    memr: Jak2MemoryReader

    # And two associated tasks, so we have handles on them.
    repl_task: asyncio.Task
    memr_task: asyncio.Task

    # Storing some information for writing save slot identifiers.
    slot_seed: str

    def __init__(self, server_address: str | None, password: str | None) -> None:
        self.repl = Jak2ReplClient(self.on_log_error,
                                   self.on_log_warn,
                                   self.on_log_success,
                                   self.on_log_info)
        self.memr = Jak2MemoryReader(self.on_location_check,
                                     self.on_finish_check,
                                     self.on_log_error,
                                     self.on_log_warn,
                                     self.on_log_success,
                                     self.on_log_info)
        # self.repl.load_data()
        # self.memr.load_data()
        super().__init__(server_address, password)

    def run_gui(self):
        from kvui import GameManager

        class Jak2Manager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Jak II ArchipelaGOAL Client"

        self.ui = Jak2Manager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super(Jak2Context, self).server_auth(password_requested)
        await self.get_username()
        self.tags = set()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):

        if cmd == "RoomInfo":
            self.slot_seed = args["seed_name"]

        if cmd == "Connected":
            slot_data = args["slot_data"]

            # Connected packet is unaware of starting inventory or if player is returning to an existing game.
            # Set initial_item_count to 0, see below comments for more info.
            if not self.repl.received_initial_items and self.repl.initial_item_count < 0:
                self.repl.initial_item_count = 0

            create_task_log_exception(self.repl.setup_options(
                self.auth[:16],
                self.slot_seed[:8]))

        if cmd == "ReceivedItems":

            # If you have a starting inventory or are returning to a game where you have items, a ReceivedItems will be
            # in the same network packet as Connected. This guarantees it is the first of any ReceivedItems we process.
            # In this case, we should set the initial_item_count to > 0, even if already set to 0 by Connected, as well
            # as the received_initial_items flag. Finally, use send_connection_status to tell the player to wait while
            # we process the initial items. However, we will skip all this if there was no initial ReceivedItems and
            # the REPL indicates it already handled any initial items (0 or otherwise).
            if not self.repl.received_initial_items and not self.repl.processed_initial_items:
                self.repl.received_initial_items = True
                self.repl.initial_item_count = len(args["items"])
                create_task_log_exception(self.repl.send_connection_status("wait"))

            # This enumeration should run on every ReceivedItems packet,
            # regardless of it being on initial connection or midway through a game.
            for index, item in enumerate(args["items"], start=args["index"]):
                logger.debug(f"index: {str(index)}, item: {str(item)}")
                self.repl.item_inbox[index] = item

    async def json_to_game_text(self, args: dict):
        if "type" in args and args["type"] in {"ItemSend"}:
            my_item_name: str | None = None
            my_item_finder: str | None = None
            their_item_name: str | None = None
            their_item_owner: str | None = None

            item = args["item"]
            recipient = args["receiving"]

            # Receiving an item from the server.
            if self.slot_concerns_self(recipient):
                my_item_name = self.item_names.lookup_in_game(item.item)

                # Did we find it, or did someone else?
                if self.slot_concerns_self(item.player):
                    my_item_finder = "MYSELF"
                else:
                    my_item_finder = self.player_names[item.player]

            # Sending an item to the server.
            if self.slot_concerns_self(item.player):
                their_item_name = self.item_names.lookup_in_slot(item.item, recipient)

                # Does it belong to us, or to someone else?
                if self.slot_concerns_self(recipient):
                    their_item_owner = "MYSELF"
                else:
                    their_item_owner = self.player_names[recipient]

            # Write to game display.
            self.repl.queue_game_text(my_item_name, my_item_finder, their_item_name, their_item_owner)

    # Even though N items come in as 1 ReceivedItems packet, there are still N PrintJson packets to process,
    # and they all arrive before the ReceivedItems packet does. Defer processing of these packets as
    # async tasks to speed up large releases of items.
    def on_print_json(self, args: dict) -> None:
        create_task_log_exception(self.json_to_game_text(args))
        super(Jak2Context, self).on_print_json(args)

    # We don't need an ap_inform function because check_locations solves that need.
    def on_location_check(self, location_ids: list[int]):
        create_task_log_exception(self.check_locations(location_ids))

    # CommonClient has no finished_game function, so we will have to craft our own. TODO - Update if that changes.
    async def ap_inform_finished_game(self):
        if not self.finished_game and self.memr.finished_game:
            message = [{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]
            await self.send_msgs(message)
            self.finished_game = True

    def on_finish_check(self):
        create_task_log_exception(self.ap_inform_finished_game())

    def _markup_panels(self, msg: str, c: str = None):
        color = self.jsontotextparser.color_codes[c] if c else None
        message = f"[color={color}]{msg}[/color]" if c else msg

        self.ui.log_panels["Archipelago"].on_message_markup(message)
        self.ui.log_panels["All"].on_message_markup(message)

    def on_log_error(self, lg: Logger, message: str):
        lg.error(message)
        if self.ui:
            self._markup_panels(message, "red")

    def on_log_warn(self, lg: Logger, message: str):
        lg.warning(message)
        if self.ui:
            self._markup_panels(message, "orange")

    def on_log_success(self, lg: Logger, message: str):
        lg.info(message)
        if self.ui:
            self._markup_panels(message, "green")

    def on_log_info(self, lg: Logger, message: str):
        lg.info(message)
        if self.ui:
            self._markup_panels(message)

    async def run_repl_loop(self):
        while True:
            await self.repl.main_tick()
            await asyncio.sleep(0.1)

    async def run_memr_loop(self):
        while True:
            await self.memr.main_tick()
            await asyncio.sleep(0.1)


def find_root_directory(ctx: Jak2Context):

    # The path to this file is platform-dependent.
    if Utils.is_windows:
        appdata = os.getenv("APPDATA")
        settings_path = os.path.normpath(f"{appdata}/OpenGOAL-Launcher/settings.json")
    elif Utils.is_linux:
        home = os.path.expanduser("~")
        settings_path = os.path.normpath(f"{home}/.config/OpenGOAL-Launcher/settings.json")
    elif Utils.is_macos:
        home = os.path.expanduser("~")
        settings_path = os.path.normpath(f"{home}/Library/Application Support/OpenGOAL-Launcher/settings.json")
    else:
        ctx.on_log_error(logger, f"Unknown operating system: {sys.platform}!")
        return

    # Boilerplate messages that all error messages in this function should have.
    err_title = "Unable to locate the ArchipelaGOAL install directory"
    alt_instructions = (f"Please verify that OpenGOAL and ArchipelaGOAL are installed properly. "
                        f"If the problem persists, follow these steps:\n"
                        f"   Run the OpenGOAL Launcher, click Jak II > Features > Mods > ArchipelaGOAL.\n"
                        f"   Then click Advanced > Open Game Data Folder.\n"
                        f"   Go up one folder, then copy this path.\n"
                        f"   Run the Archipelago Launcher, click Open host.yaml.\n"
                        f"   Set the value of 'jak2_options > root_directory' to this path.\n"
                        f"   Replace all backslashes in the path with forward slashes.\n"
                        f"   Set the value of 'jak2_options > auto_detect_root_directory' to false, "
                        f"then save and close the host.yaml file.\n"
                        f"   Close all launchers, games, clients, and console windows, then restart Archipelago.")

    if not os.path.exists(settings_path):
        msg = (f"{err_title}: The OpenGOAL settings file does not exist.\n"
               f"{alt_instructions}")
        ctx.on_log_error(logger, msg)
        return

    with open(settings_path, "r") as f:
        load = json.load(f)

        # This settings file has changed format once before, and may do so again in the future.
        # Guard against future incompatibilities by checking the file version first, and use that to determine
        # what JSON keys to look for next.
        try:
            settings_version = load["version"]
            logger.debug(f"OpenGOAL settings file version: {settings_version}")
        except KeyError:
            msg = (f"{err_title}: The OpenGOAL settings file has no version number!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        try:
            if settings_version == "2.0":
                jak2_installed = load["games"]["Jak 2"]["isInstalled"]
                mod_sources = load["games"]["Jak 2"]["modsInstalledVersion"]
            elif settings_version == "3.0":
                jak2_installed = load["games"]["jak2"]["isInstalled"]
                mod_sources = load["games"]["jak2"]["mods"]
            else:
                msg = (f"{err_title}: The OpenGOAL settings file has an unknown version number ({settings_version}).\n"
                       f"{alt_instructions}")
                ctx.on_log_error(logger, msg)
                return
        except KeyError as e:
            msg = (f"{err_title}: The OpenGOAL settings file does not contain key entry {e}!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        if not jak2_installed:
            msg = (f"{err_title}: The OpenGOAL Launcher is missing a normal install of Jak 2!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        if mod_sources is None:
            msg = (f"{err_title}: No mod sources have been configured in the OpenGOAL Launcher!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        # Mods can come from multiple user-defined sources.
        # Make no assumptions about where ArchipelaGOAL comes from, we should find it ourselves.
        archipelagoal_source = None
        for src in mod_sources:
            for mod in mod_sources[src].keys():
                if mod == "archipelagoal":
                    archipelagoal_source = src
                    # Using this file, we could verify the right version is installed, but we don't need to.
        if archipelagoal_source is None:
            msg = (f"{err_title}: The ArchipelaGOAL mod is not installed in the OpenGOAL Launcher!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        # This is just the base OpenGOAL directory, we need to go deeper.
        base_path = load["installationDir"]
        mod_relative_path = f"features/jak2/mods/{archipelagoal_source}/archipelagoal"
        mod_path = os.path.normpath(
            os.path.join(
                os.path.normpath(base_path),
                os.path.normpath(mod_relative_path)))

    return mod_path


async def run_game(ctx: Jak2Context):

    # These may already be running. If they are not running, try to start them.
    # TODO - Support other OS's. 1: Pymem is Windows-only. 2: on Linux, there's no ".exe."
    gk_running = False
    try:
        pymem.Pymem("gk.exe")  # The GOAL Kernel
        gk_running = True
    except ProcessNotFound:
        ctx.on_log_warn(logger, "Game not running, attempting to start.")

    goalc_running = False
    try:
        pymem.Pymem("goalc.exe")  # The GOAL Compiler and REPL
        goalc_running = True
    except ProcessNotFound:
        ctx.on_log_warn(logger, "Compiler not running, attempting to start.")

    try:
        auto_detect_root_directory = JakIIWorld.settings.auto_detect_root_directory
        if auto_detect_root_directory:
            root_path = find_root_directory(ctx)
        else:
            root_path = JakIIWorld.settings.root_directory

            # Always trust your instincts... the user may not have entered their root_directory properly.
            # We don't have to do this check if the root directory was auto-detected.
            if "/" not in root_path:
                msg = (f"The ArchipelaGOAL root directory contains no path. (Are you missing forward slashes?)\n"
                       f"Please check your host.yaml file.\n"
                       f"Verify the value of 'jak2_options > root_directory' is a valid existing path, "
                       f"and all backslashes have been replaced with forward slashes.")
                ctx.on_log_error(logger, msg)
                return

        # Start by checking the existence of the root directory provided in the host.yaml file (or found automatically).
        root_path = os.path.normpath(root_path)
        if not os.path.exists(root_path):
            msg = (f"The ArchipelaGOAL root directory does not exist, unable to locate the Game and Compiler.\n"
                   f"Please check your host.yaml file.\n"
                   f"If the value of 'jak2_options > auto_detect_root_directory' is true, verify that OpenGOAL "
                   f"is installed properly.\n"
                   f"If it is false, check the value of 'jak2_options > root_directory'. "
                   f"Verify it is a valid existing path, and all backslashes have been replaced with forward slashes.")
            ctx.on_log_error(logger, msg)
            return

        # Now double-check the existence of the two executables we need.
        gk_path = os.path.join(root_path, "gk.exe")
        goalc_path = os.path.join(root_path, "goalc.exe")
        if not os.path.exists(gk_path) or not os.path.exists(goalc_path):
            msg = (f"The Game and Compiler could not be found in the ArchipelaGOAL root directory.\n"
                   f"Please check your host.yaml file.\n"
                   f"If the value of 'jak2_options > auto_detect_root_directory' is true, verify that OpenGOAL "
                   f"is installed properly.\n"
                   f"If it is false, check the value of 'jak2_options > root_directory'. "
                   f"Verify it is a valid existing path, and all backslashes have been replaced with forward slashes.")
            ctx.on_log_error(logger, msg)
            return

        # Now we can FINALLY attempt to start the programs.
        if not gk_running:
            # Per-mod saves and settings are stored outside the ArchipelaGOAL root folder, so we have to traverse
            # a relative path, normalize it, and pass it in as an argument to gk. This folder will be created if
            # it does not exist.
            config_relative_path = "../_settings/archipelagoal"
            config_path = os.path.normpath(
                os.path.join(
                    root_path,
                    os.path.normpath(config_relative_path)))

            # The game freezes if text is inadvertently selected in the stdout/stderr data streams. Let's pipe those
            # streams to a file, and let's not clutter the screen with another console window.
            timestamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
            log_path = os.path.join(Utils.user_path("logs"), f"Jak2Game_{timestamp}.txt")
            log_path = os.path.normpath(log_path)
            with open(log_path, "w") as log_file:
                gk_process = subprocess.Popen(
                    [gk_path, "--game", "jak2",
                     "--config-path", config_path,
                     "--", "-v", "-boot", "-fakeiso", "-debug"],
                    stdout=log_file,
                    stderr=log_file,
                    creationflags=subprocess.CREATE_NO_WINDOW)

        if not goalc_running:
            # For the OpenGOAL Compiler, the existence of the "data" subfolder indicates you are running it from
            # a built package. This subfolder is treated as its proj_path.
            proj_path = os.path.join(root_path, "data")
            if os.path.exists(proj_path):

                # Look for "iso_data" path to automate away an oft-forgotten manual step of mod updates.
                # All relative paths should start from root_path and end with "jak2".
                goalc_args = []
                possible_relative_paths = {
                    "../../../../../active/jak2/data/iso_data/jak2",
                    "./data/iso_data/jak2",
                }

                for iso_relative_path in possible_relative_paths:
                    iso_path = os.path.normpath(
                        os.path.join(
                            root_path,
                            os.path.normpath(iso_relative_path)))

                    if os.path.exists(iso_path):
                        goalc_args = [goalc_path, "--game", "jak2", "--proj-path", proj_path, "--iso-path", iso_path]
                        logger.debug(f"iso_data folder found: {iso_path}")
                        break
                    else:
                        logger.debug(f"iso_data folder not found, continuing: {iso_path}")

                if not goalc_args:
                    msg = (f"The iso_data folder could not be found.\n"
                           f"Please follow these steps:\n"
                           f"   Run the OpenGOAL Launcher, click Jak II > Advanced > Open Game Data Folder.\n"
                           f"   Copy the iso_data folder from this location.\n"
                           f"   Click Jak II > Features > Mods > ArchipelaGOAL > Advanced > "
                           f"Open Game Data Folder.\n"
                           f"   Paste the iso_data folder in this location.\n"
                           f"   Click Advanced > Compile. When this is done, click Continue.\n"
                           f"   Close all launchers, games, clients, and console windows, then restart Archipelago.\n"
                           f"(See Setup Guide for more details.)")
                    ctx.on_log_error(logger, msg)
                    return

            # The non-existence of the "data" subfolder indicates you are running it from source, as a developer.
            # The compiler will traverse upward to find the project path on its own. It will also assume your
            # "iso_data" folder is at the root of your repository. Therefore, we don't need any of those arguments.
            else:
                goalc_args = [goalc_path, "--game", "jak2"]

            # This needs to be a new console. The REPL console cannot share a window with any other process.
            goalc_process = subprocess.Popen(goalc_args, creationflags=subprocess.CREATE_NEW_CONSOLE)

    except AttributeError as e:
        if " " in e.args[0]:
            # YAML keys in Host.yaml ought to contain no spaces, which means this is a much more important error.
            ctx.on_log_error(logger, e.args[0])
        else:
            ctx.on_log_error(logger,
                             f"Host.yaml does not contain {e.args[0]}, unable to locate game executables.")
        return
    except FileNotFoundError as e:
        msg = (f"The following path could not be found: {e.filename}\n"
               f"Please check your host.yaml file.\n"
               f"If the value of 'jak2_options > auto_detect_root_directory' is true, verify that OpenGOAL "
               f"is installed properly.\n"
               f"If it is false, check the value of 'jak2_options > root_directory'."
               f"Verify it is a valid existing path, and all backslashes have been replaced with forward slashes.")
        ctx.on_log_error(logger, msg)
        return

    # Auto connect the repl and memr agents. Sleep 5 because goalc takes just a little bit of time to load,
    # and it's not something we can await.
    ctx.on_log_info(logger, "This may take a bit... Wait for the game's title sequence before continuing!")
    await asyncio.sleep(5)
    ctx.repl.initiated_connect = True
    ctx.memr.initiated_connect = True


async def main():
    Utils.init_logging("Jak2Client", exception_logger="Client")

    ctx = Jak2Context(None, None)
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    ctx.repl_task = create_task_log_exception(ctx.run_repl_loop())
    ctx.memr_task = create_task_log_exception(ctx.run_memr_loop())

    if gui_enabled:
        ctx.run_gui()
    ctx.run_cli()

    # Find and run the game (gk) and compiler/repl (goalc).
    create_task_log_exception(run_game(ctx))
    await ctx.exit_event.wait()
    await ctx.shutdown()


def launch():
    # use colorama to display colored text highlighting
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()
