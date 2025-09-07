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

# Jak 2 imports
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

    def _cmd_repl(self, *arguments: str):
        """Sends a command to the OpenGOAL REPL. Arguments:
        - connect : connect the client to the REPL (goalc).
        - status : check internal status of the REPL.
        - test : test REPL connection by sending a simple command.
        - debug : enable debug mode for REPL communication.
        - debugoff : disable debug mode for REPL communication.
        - send <command> : send a raw GOAL command to the REPL.
        - refresh : force refresh of items to be sent to game."""
        if arguments:
            if arguments[0] == "connect":
                self.ctx.on_log_info(logger, "This may take a bit... Wait for the success audio cue before continuing!")
                self.ctx.repl.initiated_connect = True
            elif arguments[0] == "status":
                create_task_log_exception(self.ctx.repl.print_status())
            elif arguments[0] == "test":
                create_task_log_exception(self.ctx.repl.test_connection())
            elif arguments[0] == "debug":
                self.ctx.repl.enable_debug_mode()
                self.ctx.on_log_success(logger, "REPL debug mode enabled")
            elif arguments[0] == "debugoff":
                self.ctx.repl.disable_debug_mode()
                self.ctx.on_log_info(logger, "REPL debug mode disabled")
            elif arguments[0] == "send" and len(arguments) > 1:
                command = " ".join(arguments[1:])
                create_task_log_exception(self.ctx.repl.debug_send_command(command))
            elif arguments[0] == "refresh":
                create_task_log_exception(self.ctx.repl.force_item_refresh())
            else:
                self.ctx.on_log_warn(logger, f"Unknown REPL command: {arguments[0]}")

    def _cmd_memr(self, *arguments: str):
        """Sends a command to the Memory Reader. Arguments:
        - connect : connect the memory reader to the game process (gk).
        - status : check the internal status of the Memory Reader.
        - debug : enable debug mode and show comprehensive diagnostics.
        - debugoff : disable debug mode.
        - analyze : run comprehensive debug analysis (implies debug mode).
        - test : test memory connection by reading structure version.
        - refresh : force refresh memory read and check for new locations.
        - missions : show current mission completion status.
        - structure : display memory structure layout and offsets.
        - monitor : start real-time monitoring of memory values (toggle on/off)."""
        if arguments:
            if arguments[0] == "connect":
                self.ctx.memr.initiated_connect = True
            elif arguments[0] == "status":
                create_task_log_exception(self.ctx.memr.print_status())
            elif arguments[0] == "debug":
                self.ctx.memr.enable_debug_mode()
                if self.ctx.memr.connected:
                    create_task_log_exception(self.ctx.memr.print_debug_info())
            elif arguments[0] == "debugoff":
                self.ctx.memr.disable_debug_mode()
            elif arguments[0] == "analyze":
                self.ctx.memr.enable_debug_mode()
                create_task_log_exception(self.ctx.memr.print_debug_info())
            elif arguments[0] == "test":
                create_task_log_exception(self.ctx.memr.test_memory_connection())
            elif arguments[0] == "refresh":
                create_task_log_exception(self.ctx.memr.force_memory_refresh())
            elif arguments[0] == "missions":
                create_task_log_exception(self.ctx.memr.display_mission_status())
            elif arguments[0] == "structure":
                create_task_log_exception(self.ctx.memr.display_structure_info())
            elif arguments[0] == "monitor":
                self.ctx.memr.toggle_realtime_monitoring()
            else:
                self.ctx.on_log_warn(logger, f"Unknown memory reader command: {arguments[0]}")

    def _cmd_debug(self, *arguments: str):
        """Global debug commands. Arguments:
        - status : show status of all systems (REPL, Memory Reader, connections).
        - on : enable debug mode for all systems.
        - off : disable debug mode for all systems.
        - test : run comprehensive connection tests for all systems.
        - info : display detailed information about current game state."""
        if not arguments:
            # Default: show overall debug status
            create_task_log_exception(self.ctx.show_debug_status())
            return

        if arguments[0] == "status":
            create_task_log_exception(self.ctx.show_debug_status())
        elif arguments[0] == "on":
            self.ctx.repl.enable_debug_mode()
            self.ctx.memr.enable_debug_mode()
            self.ctx.on_log_success(logger, "Global debug mode enabled for all systems")
        elif arguments[0] == "off":
            self.ctx.repl.disable_debug_mode()
            self.ctx.memr.disable_debug_mode()
            self.ctx.on_log_info(logger, "Global debug mode disabled for all systems")
        elif arguments[0] == "test":
            create_task_log_exception(self.ctx.run_comprehensive_tests())
        elif arguments[0] == "info":
            create_task_log_exception(self.ctx.show_game_state_info())
        else:
            self.ctx.on_log_warn(logger, f"Unknown debug command: {arguments[0]}")


class Jak2Context(CommonContext):
    game = jak2_name
    items_handling = 0b111  # Full item handling
    command_processor = Jak2ClientCommandProcessor

    # Two agents working in tandem to handle two-way communication with the game
    # The REPL Client handles server->game direction by issuing commands to the running game
    # The Memory Reader handles game->server direction by reading memory structures
    repl: Jak2ReplClient
    memr: Jak2MemoryReader

    # Associated tasks for the agents
    repl_task: asyncio.Task
    memr_task: asyncio.Task

    # Storing information for save slot identification
    slot_seed: str

    def __init__(self, server_address: str | None, password: str | None) -> None:
        print("🚀 [CLIENT] === JAK 2 ARCHIPELAGO CLIENT INITIALIZING ===\n")
        print("📝 [CLIENT] Setting up REPL client (for sending items to game)...")
        self.repl = Jak2ReplClient(self.on_log_error,
                                   self.on_log_warn,
                                   self.on_log_success,
                                   self.on_log_info)
        print("✅ [CLIENT] REPL client initialized")
        
        print("📝 [CLIENT] Setting up Memory Reader (for reading game progress)...")
        self.memr = Jak2MemoryReader(self.on_location_check,
                                     self.on_finish_check,
                                     self.on_log_error,
                                     self.on_log_warn,
                                     self.on_log_success,
                                     self.on_log_info)
        print("✅ [CLIENT] Memory Reader initialized")
        print("🟢 [CLIENT] === JAK 2 ARCHIPELAGO CLIENT READY ===\n")
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
            
            # Set up initial item tracking
            if not self.repl.received_initial_items and self.repl.initial_item_count < 0:
                self.repl.initial_item_count = 0

            create_task_log_exception(
                self.repl.setup_options(self.auth[:16],  # The slot name
                                        self.slot_seed[:8]))

        if cmd == "ReceivedItems":
            # Handle initial items on connection
            if not self.repl.received_initial_items and not self.repl.processed_initial_items:
                self.repl.received_initial_items = True
                self.repl.initial_item_count = len(args["items"])
                create_task_log_exception(self.repl.send_connection_status("wait"))

            # Add all items to the inbox for processing
            for index, item in enumerate(args["items"], start=args["index"]):
                logger.debug(f"index: {str(index)}, item: {str(item)}")
                self.repl.item_inbox[index] = item

    async def json_to_game_text(self, args: dict):
        """Handle item send/receive messages for display in game."""
        if "type" in args and args["type"] in {"ItemSend"}:
            my_item_name: str | None = None
            my_item_finder: str | None = None
            their_item_name: str | None = None
            their_item_owner: str | None = None

            item = args["item"]
            recipient = args["receiving"]

            # Receiving an item from the server
            if self.slot_concerns_self(recipient):
                my_item_name = self.item_names.lookup_in_game(item.item)

                # Did we find it, or did someone else?
                if self.slot_concerns_self(item.player):
                    my_item_finder = "MYSELF"
                else:
                    my_item_finder = self.player_names[item.player]

            # Sending an item to the server
            if self.slot_concerns_self(item.player):
                their_item_name = self.item_names.lookup_in_slot(item.item, recipient)

                # Does it belong to us, or to someone else?
                if self.slot_concerns_self(recipient):
                    their_item_owner = "MYSELF"
                else:
                    their_item_owner = self.player_names[recipient]

            # Queue text for game display
            self.repl.queue_game_text(my_item_name, my_item_finder, their_item_name, their_item_owner)

    def on_print_json(self, args: dict) -> None:
        create_task_log_exception(self.json_to_game_text(args))
        super(Jak2Context, self).on_print_json(args)

    def on_location_check(self, location_ids: list[int]):
        if location_ids:
            print(f"📍 [CLIENT] Checking {len(location_ids)} locations with server: {location_ids}")
        create_task_log_exception(self.check_locations(location_ids))

    async def ap_inform_finished_game(self):
        """Inform the server when the game is completed."""
        if not self.finished_game and self.memr.finished_game:
            message = [{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}]
            await self.send_msgs(message)
            self.finished_game = True

    def on_finish_check(self):
        print("🏆 [CLIENT] Game completion detected - notifying server!")
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
        print("🔄 [CLIENT] Starting REPL communication loop...")
        while True:
            await self.repl.main_tick()
            await asyncio.sleep(0.1)

    async def run_memr_loop(self):
        print("🔄 [CLIENT] Starting Memory Reader loop...")
        while True:
            await self.memr.main_tick()
            await asyncio.sleep(0.1)
    
    async def show_debug_status(self):
        """Show comprehensive debug status for all systems."""
        self.on_log_info(logger, "=== COMPREHENSIVE DEBUG STATUS ===")
        
        # REPL Status
        self.on_log_info(logger, "\nREPL Client:")
        self.on_log_info(logger, f"  Connected: {self.repl.connected}")
        self.on_log_info(logger, f"  Debug Mode: {getattr(self.repl, 'debug_enabled', False)}")
        self.on_log_info(logger, f"  Address: {self.repl.ip}:{self.repl.port}")
        self.on_log_info(logger, f"  Items Processed: {self.repl.inbox_index}")
        self.on_log_info(logger, f"  Items Pending: {len(self.repl.item_inbox) - self.repl.inbox_index}")
        
        # Memory Reader Status
        self.on_log_info(logger, "\nMemory Reader:")
        self.on_log_info(logger, f"  Connected: {self.memr.connected}")
        self.on_log_info(logger, f"  Debug Mode: {self.memr.debug_enabled}")
        proc_id = str(self.memr.gk_process.process_id) if self.memr.gk_process else "None"
        self.on_log_info(logger, f"  Game Process ID: {proc_id}")
        self.on_log_info(logger, f"  Goal Address: {hex(self.memr.goal_address) if self.memr.goal_address else 'None'}")
        self.on_log_info(logger, f"  Locations Found: {len(self.memr.location_outbox)}")
        self.on_log_info(logger, f"  Game Finished: {self.memr.finished_game}")
        
        # Overall Status
        self.on_log_info(logger, "\nOverall Status:")
        self.on_log_info(logger, f"  Server Connected: {self.server and self.server.socket.connected if hasattr(self, 'server') and self.server else False}")
        self.on_log_info(logger, f"  Slot Name: {getattr(self, 'auth', 'Not Connected')}")
        self.on_log_info(logger, f"  Seed Name: {getattr(self, 'slot_seed', 'Unknown')}")
        
        self.on_log_info(logger, "=" * 40)
    
    async def run_comprehensive_tests(self):
        """Run comprehensive tests for all systems."""
        self.on_log_info(logger, "\n=== RUNNING COMPREHENSIVE TESTS ===")
        
        # Test REPL connection
        self.on_log_info(logger, "\n1. Testing REPL Connection...")
        await self.repl.test_connection()
        
        # Test Memory Reader connection
        self.on_log_info(logger, "\n2. Testing Memory Reader Connection...")
        await self.memr.test_memory_connection()
        
        # Test Memory Structure
        self.on_log_info(logger, "\n3. Testing Memory Structure...")
        await self.memr.display_structure_info()
        
        # Test Mission Status
        self.on_log_info(logger, "\n4. Testing Mission Status...")
        await self.memr.display_mission_status()
        
        self.on_log_info(logger, "\n=== COMPREHENSIVE TESTS COMPLETE ===")
    
    async def show_game_state_info(self):
        """Display detailed information about the current game state."""
        self.on_log_info(logger, "\n=== CURRENT GAME STATE INFO ===")
        
        if not self.memr.connected:
            self.on_log_warn(logger, "Memory Reader not connected - cannot read game state")
            return
        
        try:
            # Read current game state
            await self.memr.force_memory_refresh()
            
            # Show mission progress
            await self.memr.display_mission_status()
            
            # Show item status
            self.on_log_info(logger, f"\nItem Status:")
            self.on_log_info(logger, f"  Items in inbox: {len(self.repl.item_inbox)}")
            self.on_log_info(logger, f"  Items processed: {self.repl.inbox_index}")
            self.on_log_info(logger, f"  Items pending: {len(self.repl.item_inbox) - self.repl.inbox_index}")
            
            self.on_log_info(logger, "\n=== GAME STATE INFO COMPLETE ===")
            
        except Exception as e:
            self.on_log_error(logger, f"Error reading game state: {e}")


def find_root_directory(ctx: Jak2Context):
    """Find the ArchipelaGOAL installation directory for Jak 2."""
    # Same logic as Jak 1, but looking for Jak 2 mod
    
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

    err_title = "Unable to locate the ArchipelaGOAL installation directory"
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

        # Look for ArchipelaGOAL mod
        archipelagoal_source = None
        for src in mod_sources:
            for mod in mod_sources[src].keys():
                if mod == "archipelagoal":
                    archipelagoal_source = src
        if archipelagoal_source is None:
            msg = (f"{err_title}: The ArchipelaGOAL mod is not installed in the OpenGOAL Launcher!\n"
                   f"{alt_instructions}")
            ctx.on_log_error(logger, msg)
            return

        # Build the mod path
        base_path = load["installationDir"]
        mod_relative_path = f"features/jak2/mods/{archipelagoal_source}/archipelagoal"
        mod_path = os.path.normpath(
            os.path.join(
                os.path.normpath(base_path),
                os.path.normpath(mod_relative_path)))

    return mod_path


async def run_game(ctx: Jak2Context):
    """Start the Jak 2 game and compiler if they're not running."""
    
    # Check if processes are already running
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
        # For now, use a simple root directory assumption
        # TODO: Add proper settings support like Jak 1
        root_path = "C:/Program Files/OpenGOAL/features/jak2/mods/archipelagoal/archipelagoal"
        
        if not os.path.exists(root_path):
            ctx.on_log_info(logger, f"ArchipelaGOAL Jak 2 not found at: {root_path}")
            ctx.on_log_info(logger, "Auto-launch disabled. Please start the game and compiler manually.")
            ctx.on_log_info(logger, "Instructions:")
            ctx.on_log_info(logger, "1. Run the OpenGOAL Launcher")
            ctx.on_log_info(logger, "2. Click Jak II > Features > Mods > ArchipelaGOAL")
            ctx.on_log_info(logger, "3. Click Advanced > Play in Debug Mode")
            ctx.on_log_info(logger, "4. Click Advanced > Open REPL")
            return

        # Start game if not running
        if not gk_running:
            gk_path = os.path.join(root_path, "gk.exe")
            if os.path.exists(gk_path):
                config_relative_path = "../_settings/archipelagoal"
                config_path = os.path.normpath(os.path.join(root_path, config_relative_path))

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

        # Start compiler if not running
        if not goalc_running:
            goalc_path = os.path.join(root_path, "goalc.exe")
            if os.path.exists(goalc_path):
                proj_path = os.path.join(root_path, "data")
                if os.path.exists(proj_path):
                    # Look for iso_data
                    possible_iso_paths = [
                        os.path.join(root_path, "../../../../../active/jak2/data/iso_data/jak2"),
                        os.path.join(root_path, "./data/iso_data/jak2"),
                    ]
                    
                    goalc_args = None
                    for iso_path in possible_iso_paths:
                        iso_path = os.path.normpath(iso_path)
                        if os.path.exists(iso_path):
                            goalc_args = [goalc_path, "--game", "jak2", "--proj-path", proj_path, "--iso-path", iso_path]
                            logger.debug(f"iso_data folder found: {iso_path}")
                            break
                    
                    if not goalc_args:
                        ctx.on_log_error(logger, "Could not find Jak 2 iso_data folder!")
                        return
                else:
                    goalc_args = [goalc_path, "--game", "jak2"]

                goalc_process = subprocess.Popen(goalc_args, creationflags=subprocess.CREATE_NEW_CONSOLE)

    except Exception as e:
        ctx.on_log_error(logger, f"Failed to start Jak 2 processes: {e}")
        return

    # Auto-connect the agents after a delay
    ctx.on_log_info(logger, "This may take a bit... Wait for the game's title sequence before continuing!")
    await asyncio.sleep(5)
    ctx.repl.initiated_connect = True
    ctx.memr.initiated_connect = True


async def main():
    print("🚀 [MAIN] === STARTING JAK 2 ARCHIPELAGO CLIENT ===\n")
    Utils.init_logging("Jak2Client", exception_logger="Client")
    print("📝 [MAIN] Logging initialized")

    print("📝 [MAIN] Creating Jak2 context...")
    ctx = Jak2Context(None, None)
    
    print("📝 [MAIN] Starting server connection task...")
    ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
    
    print("📝 [MAIN] Starting REPL and Memory Reader tasks...")
    ctx.repl_task = create_task_log_exception(ctx.run_repl_loop())
    ctx.memr_task = create_task_log_exception(ctx.run_memr_loop())

    if gui_enabled:
        print("🖥️  [MAIN] Starting GUI...")
        ctx.run_gui()
    else:
        print("💻 [MAIN] Running in CLI mode (no GUI)")
    
    print("💻 [MAIN] Starting CLI interface...")
    ctx.run_cli()

    # Find and run the game and compiler
    print("🎮 [MAIN] Attempting to start game and compiler...")
    create_task_log_exception(run_game(ctx))
    
    print("✅ [MAIN] Client is now running! Available debug commands:")
    print("ℹ️  [MAIN] Use '/debug' for overall status and '/debug test' for comprehensive tests")
    print("ℹ️  [MAIN] Use '/memr connect' and '/repl connect' to connect to game")
    print("ℹ️  [MAIN] Use '/memr debug' and '/repl debug' to enable verbose output")
    print("ℹ️  [MAIN] Use '/memr missions' to see mission completion status")
    print("ℹ️  [MAIN] Use '/memr monitor' to toggle real-time memory monitoring")
    print("\n" + "=" * 60)
    
    await ctx.exit_event.wait()
    
    print("🛑 [MAIN] Shutting down Jak 2 client...")
    await ctx.shutdown()


def launch():
    colorama.just_fix_windows_console()
    asyncio.run(main())
    colorama.deinit()


if __name__ == "__main__":
    launch()