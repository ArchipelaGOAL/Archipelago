import logging
import struct
from typing import ByteString, Callable
import json
import pymem
from pymem import pattern
from pymem.exception import ProcessNotFound, ProcessError, MemoryReadError, WinAPIError
from dataclasses import dataclass

from worlds.jakii.locs.mission_locations import main_tasks_to_missions, side_tasks_to_missions

logger = logging.getLogger("Jak2MemoryReader")


# Some helpful constants.
sizeof_uint64 = 8
sizeof_uint32 = 4
sizeof_uint8 = 1
sizeof_float = 4


# *****************************************************************************
# **** This number must match (-> *ap-info-jak2* version) in ap-struct.gc! ****
# *****************************************************************************
expected_memory_version = 4


# IMPORTANT: OpenGOAL memory structures are particular about the alignment, in memory, of member elements according to
# their size in bits. The address for an N-bit field must be divisible by N. Use this class to define the memory offsets
# of important values in the struct. It will also do the byte alignment properly for you.
# See https://opengoal.dev/docs/reference/type_system/#arrays
@dataclass
class OffsetFactory:
    current_offset: int = 0

    def define(self, size: int, length: int = 1) -> int:

        # If necessary, align current_offset to the current size first.
        bytes_to_alignment = self.current_offset % size
        if bytes_to_alignment != 0:
            self.current_offset += (size - bytes_to_alignment)

        # Increment current_offset so the next definition can be made.
        offset_to_use = self.current_offset
        self.current_offset += (size * length)
        return offset_to_use


# Start defining important memory address offsets here. They must be in the same order, have the same sizes, and have
# the same lengths, as defined in `ap-info-jak2`.
offsets = OffsetFactory()

# Memory version (uint32 in GOAL)
memory_version_offset = offsets.define(sizeof_uint32)

# Mission information (uint in GOAL = uint64 in C++)
# Note: In GOAL, 'uint' is 8 bytes (64-bit), while 'uint32' is 4 bytes
next_mission_index_offset = offsets.define(sizeof_uint64)
next_side_mission_index_offset = offsets.define(sizeof_uint64)

# Arrays of mission IDs (uint32 arrays)
missions_checked_offset = offsets.define(sizeof_uint32, 75)
side_missions_checked_offset = offsets.define(sizeof_uint32, 35)

# Connection status (added in version 2)
connection_status_offset = offsets.define(sizeof_uint32)  # ap-connection-status enum

# Completion Information
completion_goal_type_offset = offsets.define(sizeof_uint32)
completion_goal_value_offset = offsets.define(sizeof_uint32)
completed_offset = offsets.define(sizeof_uint8)

# Deathlink Information
death_count_offset = offsets.define(sizeof_uint32)
cause_of_death_offset = offsets.define(sizeof_uint8)
deathlink_enabled_offset = offsets.define(sizeof_uint8)

# End marker (uint8 array of 4 bytes - "end\0")
end_marker_offset = offsets.define(sizeof_uint8, 4)


# Can't believe this is easier to do in GOAL than Python but that's how it be sometimes.
def as_float(value: int) -> int:
    return int(struct.unpack('f', value.to_bytes(sizeof_float, "little"))[0])


class Jak2MemoryReader:
    marker: ByteString
    goal_address: int | None = None
    connected: bool = False
    initiated_connect: bool = False

    # The memory reader just needs the game running.
    gk_process: pymem.process = None

    location_outbox: list[int] = []
    outbox_index: int = 0
    finished_game: bool = False

    # Game-related callbacks (inform the AP server of changes to game state)
    inform_checked_location: Callable
    inform_finished_game: Callable
    inform_died: Callable

    # Logging callbacks
    # These will write to the provided logger, as well as the Client GUI with color markup.
    log_error: Callable    # Red
    log_warn: Callable     # Orange
    log_success: Callable  # Green
    log_info: Callable     # White (default)

    def __init__(self,
                 location_check_callback: Callable,
                 finish_game_callback: Callable,
                 log_error_callback: Callable,
                 log_warn_callback: Callable,
                 log_success_callback: Callable,
                 log_info_callback: Callable,
                 marker: ByteString = b'ArChIpElAgO_JaK2\x00'):
        self.marker = marker

        self.inform_checked_location = location_check_callback
        self.inform_finished_game = finish_game_callback

        self.log_error = log_error_callback
        self.log_warn = log_warn_callback
        self.log_success = log_success_callback
        self.log_info = log_info_callback

    async def main_tick(self):
        if self.initiated_connect:
            await self.connect()
            self.initiated_connect = False

        if self.connected:
            try:
                self.gk_process.read_bool(self.gk_process.base_address)  # Ping to see if it's alive.
            except (ProcessError, MemoryReadError, WinAPIError):
                msg = (f"Error reading game memory! (Did the game crash?)\n"
                       f"Please close all open windows and reopen the Jak II Client "
                       f"from the Archipelago Launcher.\n"
                       f"If the game and compiler do not restart automatically, please follow these steps:\n"
                       f"   Run the OpenGOAL Launcher, click Jak II > Features > Mods > ArchipelaGOAL.\n"
                       f"   Then click Advanced > Play in Debug Mode.\n"
                       f"   Then click Advanced > Open REPL.\n"
                       f"   Then close and reopen the Jak II Client from the Archipelago Launcher.")
                self.log_error(logger, msg)
                self.connected = False
        else:
            return

        if self.connected:
            # Read the memory address to check the state of the game.
            self.read_memory()

            # Checked Locations in game. Handle the entire outbox every tick until we're up to speed.
            if len(self.location_outbox) > self.outbox_index:
                self.inform_checked_location(self.location_outbox)
                self.save_data()
                self.outbox_index += 1

            if self.finished_game:
                self.inform_finished_game()

    async def connect(self):
        try:
            self.gk_process = pymem.Pymem("gk.exe")  # The GOAL Kernel
            logger.debug("Found the gk process: " + str(self.gk_process.process_id))
        except ProcessNotFound:
            self.log_error(logger, "Could not find the game process.")
            self.connected = False
            return

        # If we don't find the marker in the first loaded module, we've failed.
        modules = list(self.gk_process.list_modules())
        logger.debug(f"Found {len(modules)} modules to search through.")
        for i, module in enumerate(modules):
            marker_address = pattern.pattern_scan_module(self.gk_process.process_handle, module, self.marker)
            if marker_address:
                # At this address is another address that contains the struct we're looking for: the game's state.
                # From here we need to add the length in bytes for the marker and 4 bytes of padding,
                # and the struct address is 8 bytes long (it's an uint64).
                goal_pointer = marker_address + len(self.marker) + 7
                self.goal_address = int.from_bytes(self.gk_process.read_bytes(goal_pointer, sizeof_uint64),
                                                   byteorder="little",
                                                   signed=False)
                logger.debug("Found the archipelago memory address: " + str(self.goal_address))
                await self.verify_memory_version()
                break
            else:
                self.log_warn(logger, f"Could not find the Archipelago marker address in module {i}, continuing...")
        else:
            self.log_warn(logger, f"Could not find the Archipelago marker address in any module!")
            self.connected = False

    async def verify_memory_version(self):
        if self.goal_address is None:
            self.log_error(logger, "Could not find the Archipelago memory address!")
            self.connected = False
            return

        memory_version: int | None = None
        try:
            memory_version = self.read_goal_address(memory_version_offset, sizeof_uint32)
            if memory_version == expected_memory_version:
                self.log_success(logger, "The Memory Reader is ready!")
                self.connected = True
            else:
                raise MemoryReadError(memory_version_offset, sizeof_uint32)
        except (ProcessError, MemoryReadError, WinAPIError):
            if memory_version is None:
                msg = (f"Could not find a version number in the OpenGOAL memory structure!\n"
                       f"   Expected Version: {str(expected_memory_version)}\n"
                       f"   Found Version: {str(memory_version)}\n"
                       f"Please follow these steps:\n"
                       f"   If the game is running, try entering '/memr connect' in the client.\n"
                       f"   You should see 'The Memory Reader is ready!'\n"
                       f"   If that did not work, or the game is not running, run the OpenGOAL Launcher.\n"
                       f"   Click Jak II > Features > Mods > ArchipelaGOAL.\n"
                       f"   Then click Advanced > Play in Debug Mode.\n"
                       f"   Try entering '/memr connect' in the client again.")
            else:
                msg = (f"The OpenGOAL memory structure is incompatible with the current Archipelago client!\n"
                       f"   Expected Version: {str(expected_memory_version)}\n"
                       f"   Found Version: {str(memory_version)}\n"
                       f"Please follow these steps:\n"
                       f"   Run the OpenGOAL Launcher, click Jak II > Features > Mods > ArchipelaGOAL.\n"
                       f"   Click Update (if one is available).\n"
                       f"   Click Advanced > Compile. When this is done, click Continue.\n"
                       f"   Click Versions and verify the latest version is marked 'Active'.\n"
                       f"   Close all launchers, games, clients, and console windows, then restart Archipelago.")
            self.log_error(logger, msg)
            self.connected = False

    async def print_status(self):
        proc_id = str(self.gk_process.process_id) if self.gk_process else "None"
        last_loc = str(self.location_outbox[self.outbox_index - 1] if self.outbox_index else "None")
        msg = (f"Memory Reader Status:\n"
               f"   Game process ID: {proc_id}\n"
               f"   Game state memory address: {str(self.goal_address)}\n"
               f"   Last location checked: {last_loc}")
        await self.verify_memory_version()
        self.log_info(logger, msg)

    def read_memory(self) -> list[int]:
        try:
            # Read completed main missions
            next_mission_idx = self.read_goal_address(next_mission_index_offset, sizeof_uint64)
            for i in range(int(next_mission_idx)):
                raw_main_task_id = self.read_goal_address(missions_checked_offset + (i * sizeof_uint32),
                                                          sizeof_uint32)

                # Verify mission exists in our table
                if raw_main_task_id in main_tasks_to_missions:

                    # Translate game-task enum to Archipelago mission ID
                    main_mission_id = main_tasks_to_missions[raw_main_task_id].mission_id
                    if main_mission_id not in self.location_outbox:

                        self.location_outbox.append(main_mission_id)

                        mission_name = main_tasks_to_missions[raw_main_task_id].name
                        logger.debug(f"Mission completed! Raw game-task: {raw_main_task_id}"
                                     f" -> Mission ID: {main_mission_id}"
                                     f" -> '{mission_name}'")

            # Read completed side missions
            next_side_mission_idx = self.read_goal_address(next_side_mission_index_offset, sizeof_uint64)
            for i in range(int(next_side_mission_idx)):
                raw_side_task_id = self.read_goal_address(side_missions_checked_offset + (i * sizeof_uint32),
                                                          sizeof_uint32)

                # Verify mission exists in our table
                if raw_side_task_id in side_tasks_to_missions:

                    # Translate game-task enum to Archipelago mission ID.
                    side_mission_id = side_tasks_to_missions[raw_side_task_id].mission_id
                    if side_mission_id not in self.location_outbox:

                        self.location_outbox.append(side_mission_id)

                        side_mission_name = side_tasks_to_missions[raw_side_task_id].name
                        logger.debug(f"Side mission completed! ID: {raw_side_task_id} -> '{side_mission_name}' "
                                     f"(location: {side_mission_id})")

            completed = self.read_goal_address(completed_offset, sizeof_uint8)
            if completed > 0 and not self.finished_game:
                self.finished_game = True
                self.log_success(logger, "Congratulations! You finished the game!")

        except (ProcessError, MemoryReadError, WinAPIError):
            msg = (f"Error reading game memory! (Did the game crash?)\n"
                   f"Please close all open windows and reopen the Jak II Client "
                   f"from the Archipelago Launcher.\n"
                   f"If the game and compiler do not restart automatically, please follow these steps:\n"
                   f"   Run the OpenGOAL Launcher, click Jak II > Features > Mods > ArchipelaGOAL.\n"
                   f"   Then click Advanced > Play in Debug Mode.\n"
                   f"   Then click Advanced > Open REPL.\n"
                   f"   Then close and reopen the Jak II Client from the Archipelago Launcher.")
            self.log_error(logger, msg)
            self.connected = False

        return self.location_outbox

    def read_goal_address(self, offset: int, length: int) -> int:
        return int.from_bytes(
            self.gk_process.read_bytes(self.goal_address + offset, length),
            byteorder="little",
            signed=False)

    def save_data(self):
        with open("jakii_location_outbox.json", "w+") as f:
            dump = {
                "outbox_index": self.outbox_index,
                "location_outbox": self.location_outbox
            }
            json.dump(dump, f, indent=4)

    def load_data(self):
        try:
            with open("jakii_location_outbox.json", "r") as f:
                load = json.load(f)
                self.outbox_index = load["outbox_index"]
                self.location_outbox = load["location_outbox"]
        except FileNotFoundError:
            pass
