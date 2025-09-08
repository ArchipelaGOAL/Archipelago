import logging
import struct
import traceback
from typing import ByteString, Callable, Optional
import pymem
from pymem import pattern
from pymem.exception import ProcessNotFound, ProcessError, MemoryReadError, WinAPIError
from dataclasses import dataclass
import binascii
import time

# Handle both relative and absolute imports for flexibility
try:
    from ..locs.mission_locations import (main_mission_table, side_mission_table,
                                          side_tasks_to_missions, main_tasks_to_missions)
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from locs.mission_locations import (main_mission_table, side_mission_table,
                                        side_tasks_to_missions, tasks_to_missions)


logger = logging.getLogger("Jak2MemoryReader")


# Some helpful constants.
sizeof_uint64 = 8
sizeof_uint32 = 4
sizeof_uint8 = 1

# *****************************************************************************
# **** This number must match (-> *ap-info-jak2* version) in ap-struct.gc! ****
# *****************************************************************************
expected_memory_version = 3


# Memory structure layout for Jak 2 Archipelago integration
# Must match ap-info-jak2 structure in ap-struct-h.gc
@dataclass
class OffsetFactory:
    current_offset: int = 0

    def define(self, size: int, length: int = 1) -> int:
        # Align current_offset to the current size first
        bytes_to_alignment = self.current_offset % size
        if bytes_to_alignment != 0:
            self.current_offset += (size - bytes_to_alignment)

        # Increment current_offset so the next definition can be made
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

# End marker (uint8 array of 4 bytes - "end\0")
end_marker_offset = offsets.define(sizeof_uint8, 4)

# Debug: Print calculated offsets
logger.debug(f"Calculated structure offsets:")
logger.debug(f"  version: {memory_version_offset}")
logger.debug(f"  next_mission_index: {next_mission_index_offset}")
logger.debug(f"  next_side_mission_index: {next_side_mission_index_offset}")
logger.debug(f"  missions_checked: {missions_checked_offset}")
logger.debug(f"  side_missions_checked: {side_missions_checked_offset}")
logger.debug(f"  connection_status: {connection_status_offset}")
logger.debug(f"  end_marker: {end_marker_offset}")
logger.debug(f"  total_size: {offsets.current_offset}")


class Jak2MemoryReader:
    gk_process: pymem.process = None
    goal_address: int = None
    connected = False
    initiated_connect = False

    # Track completed missions
    location_outbox: list[int] = []
    outbox_index: int = 0
    
    # Track game completion
    finished_game = False

    # Debug state tracking
    debug_enabled = False
    marker_address: Optional[int] = None
    successful_marker: Optional[bytes] = None
    last_modules: list = None
    realtime_monitoring = False
    
    # Test both marker variants
    markers_to_test = [
        (b'ArChIpElAgO_JaK2', "without null terminator"),
        (b'ArChIpElAgO_JaK2\x00', "with null terminator")
    ]

    # Callbacks for communicating with the main client
    inform_checked_location: Callable
    inform_finished_game: Callable
    log_error: Callable
    log_warn: Callable
    log_success: Callable
    log_info: Callable

    def __init__(self,
                 location_check_callback: Callable,
                 finish_game_callback: Callable,
                 log_error_callback: Callable,
                 log_warn_callback: Callable,
                 log_success_callback: Callable,
                 log_info_callback: Callable,
                 marker: ByteString = b'ArChIpElAgO_JaK2'):
        self.marker = marker

        self.inform_checked_location = location_check_callback
        self.inform_finished_game = finish_game_callback

        self.log_error = log_error_callback
        self.log_warn = log_warn_callback
        self.log_success = log_success_callback
        self.log_info = log_info_callback
        
        # Log marker variants that will be tested
        for marker_bytes, desc in self.markers_to_test:
            logger.debug(f"Will test marker {desc}: {marker_bytes!r} (hex: {binascii.hexlify(marker_bytes).decode('ascii')})")

    async def main_tick(self):
        if self.initiated_connect:
            print("🔌 [MEMORY] Initiating connection to game...")
            await self.connect()
            self.initiated_connect = False

        if self.connected:
            try:
                self.gk_process.read_bool(self.gk_process.base_address)  # Ping to see if it's alive.
                # Uncomment for very verbose connection monitoring:
                # print("✅ [MEMORY] Connection ping successful")
            except (ProcessError, MemoryReadError, WinAPIError):
                msg = (f"Error reading game memory! (Did the game crash?)\n"
                       f"Please close all open windows and reopen the Jak II Client "
                       f"from the Archipelago Launcher.\n"
                       f"If the game and compiler do not restart automatically, please follow these steps:\n"
                       f"   Run the OpenGOAL Launcher, click Jak II > Features > Mods > ArchipelaGOAL.\n"
                       f"   Then click Advanced > Play in Debug Mode.\n"
                       f"   Then click Advanced > Open REPL.\n"
                       f"   Then close and reopen the Jak II Client from the Archipelago Launcher.")
                print(f"🔴 [MEMORY] CONNECTION LOST: {msg}")
                self.log_error(logger, msg)
                self.connected = False
        else:
            return

        if self.connected:
            # Read the memory address to check the state of the game.
            try:
                locations = self.read_memory()
                # if locations and len(locations) > 0:
                #     print(f"📍 [MEMORY] Found {len(locations)} completed locations")
            except Exception as e:
                print(f"🔴 [MEMORY] Error during memory read: {e}")

            # Handle completed missions
            if len(self.location_outbox) > self.outbox_index:
                new_locations = self.location_outbox[self.outbox_index:]
                print(f"🎯 [MEMORY] Reporting {len(new_locations)} new locations to client: {new_locations}")
                self.inform_checked_location(self.location_outbox)
                self.outbox_index += 1

            # Check for game completion (final boss defeated)
            if self.finished_game:
                print("🏁 [MEMORY] Game completion detected - informing client!")
                self.inform_finished_game()

    async def connect(self):
        """Connect to the game process with comprehensive debugging."""
        print("🔍 [MEMORY] === STARTING MEMORY READER CONNECTION ===\n")
        if self.debug_enabled:
            print("🐛 [MEMORY] Debug mode enabled - verbose output will be shown")
            self.log_info(logger, "=== Starting Memory Reader Connection with Debug Mode ===\n")
        else:
            print("ℹ️ [MEMORY] Debug mode disabled - use '/memr debug' to enable verbose output")
        
        # Step 1: Connect to process
        if not await self._connect_to_process():
            return
        
        # Step 2: Scan modules for marker
        if not await self._scan_modules_for_marker():
            return
        
        # Step 3: Analyze marker structure
        if not await self._analyze_marker_structure():
            return
        
        # Step 4: Verify memory version and structure
        await self.verify_memory_version()
        
    async def _connect_to_process(self) -> bool:
        """Connect to the gk.exe process with detailed diagnostics."""
        print("🎮 [MEMORY] Step 1: Connecting to gk.exe process...")
        try:
            self.gk_process = pymem.Pymem("gk.exe")  # The GOAL Kernel - same as Jak 1
            logger.debug("Found the gk process: " + str(self.gk_process.process_id))
            print(f"✅ [MEMORY] Found gk.exe process - PID: {self.gk_process.process_id}")
            self.log_info(logger, f"Found the gk process: PID {self.gk_process.process_id}")
            
            if self.debug_enabled:
                self.log_info(logger, f"Process handle: {self.gk_process.process_handle}")
                self.log_info(logger, f"Base address: 0x{self.gk_process.base_address:x}")
            
            return True
        except ProcessNotFound:
            print("❌ [MEMORY] Could not find gk.exe process!")
            print("❌ [MEMORY] Please make sure Jak 2 is running.")
            self.log_error(logger, "Could not find the game process (gk.exe).")
            self.log_error(logger, "Please make sure the game is running.")
            self.connected = False
            return False
        except Exception as e:
            print(f"🔴 [MEMORY] Unexpected error connecting to process: {e}")
            self.log_error(logger, f"Unexpected error connecting to process: {e}")
            if self.debug_enabled:
                print(f"🐛 [MEMORY] Traceback: {traceback.format_exc()}")
                self.log_error(logger, f"Traceback: {traceback.format_exc()}")
            self.connected = False
            return False

    async def _scan_modules_for_marker(self) -> bool:
        """Scan all process modules for the Archipelago marker."""
        print("🔍 [MEMORY] Step 2: Scanning process modules for Archipelago marker...")
        try:
            modules = list(self.gk_process.list_modules())
            self.last_modules = modules  # Store for debug access
            print(f"📦 [MEMORY] Found {len(modules)} loaded modules to scan")
            self.log_info(logger, f"Found {len(modules)} loaded modules")
            
            if self.debug_enabled:
                # List all modules with detailed info
                self.log_info(logger, "\n=== Process Module Analysis ===")
                for i, module in enumerate(modules):
                    self.log_info(logger, f"Module {i:2d}: {module.name:<20} at 0x{module.lpBaseOfDll:08x} (size: 0x{module.SizeOfImage:08x})")
            elif modules:
                main_module = modules[0]
                self.log_info(logger, f"Main module: {main_module.name} at 0x{main_module.lpBaseOfDll:x} (size: 0x{main_module.SizeOfImage:x})")
            
            # Test each marker variant across all modules
            for marker_bytes, marker_desc in self.markers_to_test:
                if self.debug_enabled:
                    marker_hex = binascii.hexlify(marker_bytes).decode('ascii')
                    self.log_info(logger, f"\n--- Testing marker {marker_desc} ---")
                    self.log_info(logger, f"Marker: {marker_bytes!r} (hex: {marker_hex})")
                
                for i, module in enumerate(modules):
                    try:
                        if self.debug_enabled:
                            self.log_info(logger, f"Scanning module {i}: {module.name}")
                        else:
                            logger.debug(f"Scanning module {i}: {module.name} for marker {marker_desc}")
                            
                        marker_address = pattern.pattern_scan_module(self.gk_process.process_handle, module, marker_bytes)
                        if marker_address:
                            self.marker_address = marker_address
                            self.successful_marker = marker_bytes
                            print(f"🎯 [MEMORY] *** FOUND MARKER {marker_desc} in {module.name} at address 0x{marker_address:x} ***")
                            self.log_success(logger, f"*** FOUND MARKER {marker_desc} in {module.name} at address 0x{marker_address:x} ***")
                            return True
                        else:
                            if self.debug_enabled:
                                self.log_info(logger, f"Marker {marker_desc} not found in {module.name}")
                    except Exception as e:
                        self.log_warn(logger, f"Failed to scan module {module.name}: {e}")
            
            # If no marker found, try partial patterns for diagnostics
            await self._scan_partial_markers(modules)
            
            print("❌ [MEMORY] Could not find the Jak 2 Archipelago marker in any module!")
            print("❌ [MEMORY] This usually means the ArchipelaGOAL mod is not loaded.")
            self.log_error(logger, "Could not find the Jak 2 Archipelago marker in any module!")
            self.connected = False
            return False
            
        except Exception as e:
            self.log_error(logger, f"Error scanning modules: {e}")
            if self.debug_enabled:
                self.log_error(logger, f"Traceback: {traceback.format_exc()}")
            self.connected = False
            return False
    
    async def _scan_partial_markers(self, modules: list):
        """Scan for partial marker patterns to help with debugging."""
        partial_patterns = [
            (b"ArChIpElAgO", "ArChIpElAgO (partial)"),
            (b"JaK2", "JaK2 (suffix)"),
            (b"ArCh", "ArCh (prefix)"),
        ]
        
        self.log_info(logger, "\n=== Trying partial marker patterns ===")
        
        for pattern_bytes, pattern_desc in partial_patterns:
            self.log_info(logger, f"Searching for: {pattern_desc} - {pattern_bytes!r}")
            
            for i, module in enumerate(modules[:3]):  # Only check first 3 modules
                try:
                    addr = pattern.pattern_scan_module(self.gk_process.process_handle, module, pattern_bytes)
                    if addr:
                        self.log_info(logger, f"Found {pattern_desc} in {module.name} at 0x{addr:x}")
                        # Read surrounding bytes for analysis
                        try:
                            surrounding = self.gk_process.read_bytes(addr, 32)
                            hex_data = binascii.hexlify(surrounding).decode('ascii')
                            self.log_info(logger, f"Surrounding bytes: {hex_data}")
                            
                            if self.debug_enabled:
                                # Show as hex dump
                                self.log_info(logger, "Hex dump of surrounding area:")
                                for j in range(0, len(surrounding), 16):
                                    chunk = surrounding[j:j+16]
                                    hex_str = ' '.join(f'{b:02x}' for b in chunk)
                                    ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                                    self.log_info(logger, f"  0x{addr + j:08x}: {hex_str:<48} |{ascii_str}|")
                        except Exception as read_e:
                            self.log_info(logger, f"Could not read surrounding bytes: {read_e}")
                except Exception as scan_e:
                    if self.debug_enabled:
                        self.log_info(logger, f"Error scanning {module.name} for {pattern_desc}: {scan_e}")
        
    async def _analyze_marker_structure(self) -> bool:
        """Analyze the memory structure at the marker address to extract the GOAL pointer."""
        print("🔬 [MEMORY] Step 3: Analyzing marker structure to find GOAL pointer...")
        if not self.marker_address:
            print("❌ [MEMORY] Marker address not found!")
            self.log_error(logger, "Marker address not found!")
            return False
        
        if self.debug_enabled:
            self.log_info(logger, f"\n=== Analyzing marker structure at 0x{self.marker_address:x} ===")
        else:
            self.log_info(logger, f"Analyzing memory structure at marker address 0x{self.marker_address:x}")
        
        try:
            # Read a larger block around the marker for analysis
            block_size = 64 if self.debug_enabled else 32
            block_bytes = self.gk_process.read_bytes(self.marker_address, block_size)
            
            if self.debug_enabled:
                self.log_info(logger, "Raw bytes at marker:")
                for i in range(0, len(block_bytes), 16):
                    chunk = block_bytes[i:i+16]
                    hex_str = ' '.join(f'{b:02x}' for b in chunk)
                    ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                    self.log_info(logger, f"  0x{self.marker_address + i:08x}: {hex_str:<48} |{ascii_str}|")
            else:
                hex_data = binascii.hexlify(block_bytes).decode('ascii')
                self.log_info(logger, f"Block bytes: {hex_data}")
            
            # Analyze the C++ struct ArchipelagoBlock layout:
            # struct ArchipelagoBlock {
            #   const char marker[17] = "ArChIpElAgO_JaK2";  // 17 bytes including null
            #   u64 pointer_to_symbol = 0;                  // 8 bytes with potential padding
            # };
            
            marker_length_in_cpp = 17  # marker[17] in C++
            found_marker_length = len(self.successful_marker) if self.successful_marker else len(self.marker)
            
            if self.debug_enabled:
                self.log_info(logger, f"Found marker length: {found_marker_length}")
                self.log_info(logger, f"C++ array length: {marker_length_in_cpp}")
            
            # Test different padding scenarios to find the correct pointer location
            padding_scenarios = [
                ("No padding", 0),
                ("1-byte alignment", 1),
                ("4-byte alignment", (4 - (marker_length_in_cpp % 4)) % 4),
                ("8-byte alignment", (8 - (marker_length_in_cpp % 8)) % 8),
            ]
            
            if self.debug_enabled:
                self.log_info(logger, "\n--- Testing different alignment scenarios ---")
            
            for scenario_name, padding in padding_scenarios:
                pointer_offset = marker_length_in_cpp + padding
                pointer_address = self.marker_address + pointer_offset
                
                if self.debug_enabled:
                    self.log_info(logger, f"\n--- Testing {scenario_name} (padding: {padding}) ---")
                    self.log_info(logger, f"Pointer offset: {pointer_offset}")
                    self.log_info(logger, f"Pointer address: 0x{pointer_address:x}")
                
                if pointer_offset + 8 <= len(block_bytes):
                    pointer_bytes = block_bytes[pointer_offset:pointer_offset + 8]
                    pointer_value = int.from_bytes(pointer_bytes, byteorder="little", signed=False)
                    
                    if self.debug_enabled:
                        self.log_info(logger, f"Pointer bytes: {binascii.hexlify(pointer_bytes).decode('ascii')}")
                        self.log_info(logger, f"Pointer value: 0x{pointer_value:x}")
                    
                    # Check if this looks like a valid pointer
                    if pointer_value != 0 and pointer_value >= 0x1000:
                        if self.debug_enabled:
                            self.log_info(logger, f"*** This looks like a valid pointer! ***")
                        
                        # Try to read from this address to verify
                        try:
                            test_read = self.gk_process.read_bytes(pointer_value, 16)
                            if self.debug_enabled:
                                test_hex = binascii.hexlify(test_read).decode('ascii')
                                self.log_info(logger, f"Data at pointer: {test_hex}")
                            
                            # Try to parse as our structure
                            if len(test_read) >= 4:
                                version = struct.unpack("<I", test_read[0:4])[0]
                                if self.debug_enabled:
                                    self.log_info(logger, f"Potential version field: {version}")
                                
                                if version == expected_memory_version:
                                    print(f"✅ [MEMORY] *** FOUND CORRECT VERSION {version}! This is the right pointer! ***")
                                    self.log_success(logger, f"*** FOUND CORRECT VERSION! This is likely the right pointer! ***")
                                    self.goal_address = pointer_value
                                    
                                    # Log the successful configuration
                                    print(f"🎯 [MEMORY] Found marker at: 0x{self.marker_address:x}")
                                    print(f"🎯 [MEMORY] Pointer location: 0x{pointer_address:x} (marker + {marker_length_in_cpp} + {padding} padding)")
                                    print(f"🎯 [MEMORY] Found the Jak 2 archipelago memory address: 0x{self.goal_address:x}")
                                    self.log_success(logger, f"Found marker at: 0x{self.marker_address:x}")
                                    self.log_success(logger, f"Pointer location: 0x{pointer_address:x} (marker + {marker_length_in_cpp} + {padding} padding)")
                                    self.log_success(logger, f"Found the Jak 2 archipelago memory address: 0x{self.goal_address:x}")
                                    return True
                                elif self.debug_enabled:
                                    self.log_info(logger, f"Version mismatch: expected {expected_memory_version}, got {version}")
                        
                        except Exception as e:
                            if self.debug_enabled:
                                self.log_info(logger, f"Could not read from pointer address: {e}")
                    elif self.debug_enabled:
                        self.log_info(logger, "Pointer value looks invalid (null or too low)")
                elif self.debug_enabled:
                    self.log_info(logger, "Pointer would be outside the read block")
            
            print("❌ [MEMORY] Could not find valid pointer to Archipelago structure")
            print("❌ [MEMORY] This might indicate a memory structure version mismatch.")
            self.log_error(logger, "Could not find valid pointer to Archipelago structure")
            self.connected = False
            return False
            
        except Exception as e:
            self.log_error(logger, f"Failed to analyze marker structure: {e}")
            if self.debug_enabled:
                self.log_error(logger, f"Traceback: {traceback.format_exc()}")
            self.connected = False
            return False

    async def verify_memory_version(self):
        print("🔍 [MEMORY] Step 4: Verifying memory structure version...")
        if self.goal_address is None:
            print("❌ [MEMORY] Could not find the Jak 2 Archipelago memory address!")
            self.log_error(logger, "Could not find the Jak 2 Archipelago memory address!")
            self.connected = False
            return

        # Debug: Print structure layout information
        self.log_info(logger, "=== Memory Structure Analysis ===")
        self.log_info(logger, f"Expected memory version: {expected_memory_version}")
        self.log_info(logger, f"Structure base address: 0x{self.goal_address:x}")
        self.log_info(logger, f"Version offset: {memory_version_offset} (0x{memory_version_offset:x})")
        
        # Debug: Read raw bytes from the beginning of the structure
        try:
            raw_bytes = self.gk_process.read_bytes(self.goal_address, 64)  # Read first 64 bytes
            hex_dump = binascii.hexlify(raw_bytes).decode('ascii')
            self.log_info(logger, f"First 64 bytes of structure: {hex_dump}")
            
            # Parse as different data types to see what we get
            for offset in range(0, min(16, len(raw_bytes) - 4), 4):
                try:
                    value_u32 = struct.unpack("<I", raw_bytes[offset:offset+4])[0]
                    self.log_info(logger, f"  Offset {offset:2d} (0x{offset:02x}): uint32 = {value_u32:10d} (0x{value_u32:08x})")
                except:
                    pass
        except Exception as e:
            self.log_error(logger, f"Could not read raw bytes from structure: {e}")

        memory_version: int | None = None
        try:
            # Try reading the version with detailed error handling
            self.log_info(logger, f"Attempting to read version at address 0x{self.goal_address + memory_version_offset:x}")
            memory_version = self.read_goal_address(memory_version_offset, sizeof_uint32)
            
            self.log_info(logger, f"Successfully read memory version: {memory_version}")
            
            if memory_version == expected_memory_version:
                print(f"✅ [MEMORY] Version match! Expected: {expected_memory_version}, Found: {memory_version}")
                print("🟢 [MEMORY] === THE JAK 2 MEMORY READER IS READY! ===\n")
                self.log_success(logger, "The Jak 2 Memory Reader is ready!")
                self.connected = True
                
                # Debug: Verify other structure fields are readable
                try:
                    next_mission_idx = self.read_goal_address(next_mission_index_offset, sizeof_uint64)
                    next_side_mission_idx = self.read_goal_address(next_side_mission_index_offset, sizeof_uint64)
                    self.log_info(logger, f"Next mission index: {next_mission_idx}")
                    self.log_info(logger, f"Next side mission index: {next_side_mission_idx}")
                except Exception as e:
                    self.log_warn(logger, f"Could not read mission indices (this may be normal): {e}")
            else:
                print(f"❌ [MEMORY] Version mismatch! Expected {expected_memory_version}, got {memory_version}")
                print("❌ [MEMORY] The ArchipelaGOAL mod version is incompatible with this client.")
                self.log_error(logger, f"Version mismatch! Expected {expected_memory_version}, got {memory_version}")
                self.connected = False
                
        except (ProcessError, MemoryReadError, WinAPIError) as e:
            print(f"🔴 [MEMORY] CRITICAL: Exception while reading memory version: {e}")
            self.log_error(logger, f"Exception while reading memory version: {e}")
            
            # Enhanced diagnostic information
            if self.debug_enabled:
                self.log_info(logger, "\n=== Enhanced Diagnostic Information ===")
                
                # Try reading with different offsets to see if we can find the version elsewhere
                self.log_info(logger, "Testing alternative version locations:")
                for test_offset in [0, 4, 8, 12, 16, 20, 24]:
                    try:
                        test_value = self.read_goal_address(test_offset, sizeof_uint32)
                        self.log_info(logger, f"  Offset {test_offset:2d}: {test_value:10d} (0x{test_value:08x})")
                        if test_value == expected_memory_version:
                            self.log_info(logger, f"  *** Found expected version at offset {test_offset}! ***")
                    except Exception as read_e:
                        self.log_info(logger, f"  Offset {test_offset:2d}: Could not read ({read_e})")
                
                # Try to read raw bytes and show hex dump
                try:
                    raw_bytes = self.gk_process.read_bytes(self.goal_address, 64)
                    self.log_info(logger, "\nRaw structure bytes:")
                    for i in range(0, len(raw_bytes), 16):
                        chunk = raw_bytes[i:i+16]
                        hex_str = ' '.join(f'{b:02x}' for b in chunk)
                        ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                        self.log_info(logger, f"  +0x{i:02x}: {hex_str:<48} |{ascii_str}|")
                except Exception as hex_e:
                    self.log_info(logger, f"Could not read raw bytes: {hex_e}")
            else:
                # Basic diagnostic for non-debug mode
                self.log_info(logger, "=== Diagnostic Information ===")
                
                # Check if we're reading from a valid memory region
                try:
                    # Try reading with different offsets to see if we can find the version elsewhere
                    for test_offset in [0, 4, 8, 12, 16]:
                        try:
                            test_value = self.read_goal_address(test_offset, sizeof_uint32)
                            self.log_info(logger, f"Test read at offset {test_offset}: {test_value}")
                            if test_value == expected_memory_version:
                                self.log_info(logger, f"Found expected version at offset {test_offset}!")
                        except:
                            self.log_info(logger, f"Could not read at offset {test_offset}")
                except:
                    pass
                
            if memory_version is None:
                msg = (f"Could not find a version number in the OpenGOAL memory structure!\n"
                       f"   Expected Version: {str(expected_memory_version)}\n"
                       f"   Found Version: {str(memory_version)}\n"
                       f"   Structure Address: 0x{self.goal_address:x}\n"
                       f"   Version Offset: {memory_version_offset} (0x{memory_version_offset:x})\n"
                       f"Please follow these steps:\n"
                       f"   1. Check that the ArchipelaGOAL mod is properly loaded in the game.\n"
                       f"   2. Try entering '/memr connect' in the client.\n"
                       f"   3. If that doesn't work, restart the game and try again.\n"
                       f"   4. Check the game console for Archipelago initialization messages.")
                print(f"🔴 [MEMORY] CRITICAL: {msg}")
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
                print(f"🔴 [MEMORY] CRITICAL: {msg}")
            self.log_error(logger, msg)
            self.connected = False

    async def print_status(self):
        """Print memory reader status with optional debug details."""
        proc_id = str(self.gk_process.process_id) if self.gk_process else "None"
        last_loc = str(self.location_outbox[self.outbox_index - 1] if self.outbox_index else "None")
        
        msg = ["Jak 2 Memory Reader Status:"]
        msg.append(f"   Connected: {self.connected}")
        msg.append(f"   Debug Mode: {self.debug_enabled}")
        msg.append(f"   Game process ID: {proc_id}")
        msg.append(f"   Game state memory address: {str(self.goal_address)}")
        msg.append(f"   Marker address: {hex(self.marker_address) if self.marker_address else 'None'}")
        successful_marker_str = repr(self.successful_marker) if self.successful_marker else 'None'
        msg.append(f"   Successful marker: {successful_marker_str}")
        msg.append(f"   Locations checked: {len(self.location_outbox)}")
        msg.append(f"   Last location checked: {last_loc}")
        msg.append(f"   Game finished: {self.finished_game}")
        
        if self.debug_enabled and self.last_modules:
            msg.append(f"   Process modules: {len(self.last_modules)}")
            if self.last_modules:
                msg.append(f"   Main module: {self.last_modules[0].name}")
        
        self.log_info(logger, "\n".join(msg))
        
        if self.connected:
            await self.verify_memory_version()
    
    async def print_debug_info(self):
        """Print comprehensive debug information about the memory connection."""
        self.log_info(logger, "\n=== COMPREHENSIVE DEBUG INFORMATION ===")
        
        # Process information
        if self.gk_process:
            self.log_info(logger, f"Process: gk.exe (PID: {self.gk_process.process_id})")
            self.log_info(logger, f"Process handle: {self.gk_process.process_handle}")
            self.log_info(logger, f"Base address: 0x{self.gk_process.base_address:x}")
        else:
            self.log_info(logger, "Process: Not connected")
        
        # Module information
        if self.last_modules:
            self.log_info(logger, f"\nModules ({len(self.last_modules)} total):")
            for i, module in enumerate(self.last_modules):
                self.log_info(logger, f"  {i:2d}: {module.name:<20} at 0x{module.lpBaseOfDll:08x} (size: 0x{module.SizeOfImage:08x})")
        
        # Marker search information
        self.log_info(logger, f"\nMarker Search:")
        for marker_bytes, desc in self.markers_to_test:
            marker_hex = binascii.hexlify(marker_bytes).decode('ascii')
            self.log_info(logger, f"  Tested {desc}: {marker_bytes!r} (hex: {marker_hex})")
        
        if self.successful_marker:
            self.log_info(logger, f"  Found: {self.successful_marker!r} at 0x{self.marker_address:x}")
        else:
            self.log_info(logger, "  Found: None")
        
        # Memory structure information
        if self.goal_address:
            self.log_info(logger, f"\nMemory Structure:")
            self.log_info(logger, f"  GOAL address: 0x{self.goal_address:x}")
            self.log_info(logger, f"  Expected version: {expected_memory_version}")
            
            try:
                # Read structure information
                await self._analyze_goal_structure_debug()
            except Exception as e:
                self.log_info(logger, f"  Error reading structure: {e}")
        else:
            self.log_info(logger, "\nMemory Structure: Not found")
        
        # Connection status summary
        self.log_info(logger, f"\nStatus Summary:")
        self.log_info(logger, f"  Connected: {self.connected}")
        self.log_info(logger, f"  Locations tracked: {len(self.location_outbox)}")
        self.log_info(logger, f"  Game finished: {self.finished_game}")
        
        self.log_info(logger, "=" * 50)
    
    async def _analyze_goal_structure_debug(self):
        """Analyze the GOAL structure layout for debugging."""
        if not self.goal_address:
            return
        
        try:
            # Read more of the structure for analysis
            structure_size = 512
            structure_bytes = self.gk_process.read_bytes(self.goal_address, structure_size)
            
            self.log_info(logger, "  First 128 bytes of structure:")
            for i in range(0, min(128, len(structure_bytes)), 16):
                chunk = structure_bytes[i:i+16]
                hex_str = ' '.join(f'{b:02x}' for b in chunk)
                ascii_str = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
                self.log_info(logger, f"    +0x{i:03x}: {hex_str:<48} |{ascii_str}|")
            
            # Parse structure fields
            self.log_info(logger, "\n  Structure field analysis:")
            
            offset = 0
            
            # Version (uint32)
            if offset + 4 <= len(structure_bytes):
                version = struct.unpack("<I", structure_bytes[offset:offset+4])[0]
                self.log_info(logger, f"    Version (offset {offset:3d}): {version}")
                offset += 4
            
            # Align to 8-byte boundary for uint fields
            if offset % 8 != 0:
                padding = 8 - (offset % 8)
                self.log_info(logger, f"    Added {padding} bytes padding for uint alignment")
                offset += padding
            
            # Next mission index (uint = 8 bytes)
            if offset + 8 <= len(structure_bytes):
                next_mission_idx = struct.unpack("<Q", structure_bytes[offset:offset+8])[0]
                self.log_info(logger, f"    Next mission index (offset {offset:3d}): {next_mission_idx}")
                offset += 8
            
            # Next side mission index (uint = 8 bytes)
            if offset + 8 <= len(structure_bytes):
                next_side_mission_idx = struct.unpack("<Q", structure_bytes[offset:offset+8])[0]
                self.log_info(logger, f"    Next side mission index (offset {offset:3d}): {next_side_mission_idx}")
                offset += 8
            
            # Show some missions if any are completed
            mission_ids = []
            for i in range(min(10, 70)):  # Show first 10 missions
                if offset + 4 <= len(structure_bytes):
                    mission_id = struct.unpack("<I", structure_bytes[offset:offset+4])[0]
                    if mission_id != 0:
                        mission_ids.append(mission_id)
                    offset += 4
                else:
                    break
            
            if mission_ids:
                self.log_info(logger, f"    Completed missions (first 10): {mission_ids}")
            else:
                self.log_info(logger, "    No completed missions found")
        
        except Exception as e:
            self.log_info(logger, f"  Error analyzing structure: {e}")
    
    def enable_debug_mode(self):
        """Enable comprehensive debug mode."""
        self.debug_enabled = True
        logger.setLevel(logging.DEBUG)
        self.log_info(logger, "Debug mode enabled - verbose diagnostics will be shown")
    
    def disable_debug_mode(self):
        """Disable debug mode."""
        self.debug_enabled = False
        self.log_info(logger, "Debug mode disabled")
    
    async def test_memory_connection(self):
        """Test memory connection by reading structure version."""
        print("🔍 [MEMORY] Testing memory connection...")
        self.log_info(logger, "Testing memory connection")
        
        if not self.connected:
            print("❌ [MEMORY] Not connected to game process - cannot test connection")
            self.log_error(logger, "Not connected to game process - cannot test connection")
            return
        
        try:
            # Test basic process connection
            self.gk_process.read_bool(self.gk_process.base_address)
            print("✅ [MEMORY] Process connection test PASSED")
            self.log_success(logger, "Process connection test PASSED")
            
            # Test memory structure access
            if self.goal_address:
                version = self.read_goal_address(memory_version_offset, sizeof_uint32)
                print(f"✅ [MEMORY] Memory structure test PASSED - Version: {version}")
                self.log_success(logger, f"Memory structure test PASSED - Version: {version}")
                
                # Test reading mission indices
                next_mission_idx = self.read_goal_address(next_mission_index_offset, sizeof_uint64)
                next_side_mission_idx = self.read_goal_address(next_side_mission_index_offset, sizeof_uint64)
                print(f"✅ [MEMORY] Mission indices test PASSED - Main: {next_mission_idx}, Side: {next_side_mission_idx}")
                self.log_success(logger, f"Mission indices test PASSED - Main: {next_mission_idx}, Side: {next_side_mission_idx}")
            else:
                print("❌ [MEMORY] Memory structure test FAILED - No goal address")
                self.log_error(logger, "Memory structure test FAILED - No goal address")
                
        except Exception as e:
            print(f"🔴 [MEMORY] Connection test ERROR: {e}")
            self.log_error(logger, f"Connection test ERROR: {e}")
    
    async def force_memory_refresh(self):
        """Force refresh memory read and check for new locations."""
        print("🔄 [MEMORY] Forcing memory refresh...")
        self.log_info(logger, "Forcing memory refresh")
        
        if not self.connected:
            print("❌ [MEMORY] Not connected to game - cannot refresh memory")
            self.log_error(logger, "Not connected to game - cannot refresh memory")
            return
        
        try:
            print(f"📊 [MEMORY] Current locations found: {len(self.location_outbox)}")
            
            # Force read memory
            locations = self.read_memory()
            
            if locations:
                new_locations_count = len(locations) - len(self.location_outbox)
                if new_locations_count > 0:
                    print(f"✨ [MEMORY] Found {new_locations_count} new locations!")
                    self.log_success(logger, f"Found {new_locations_count} new locations")
                else:
                    print("ℹ️  [MEMORY] No new locations found")
                    self.log_info(logger, "No new locations found")
            
            print(f"📊 [MEMORY] Total locations: {len(self.location_outbox)}")
            print("✅ [MEMORY] Memory refresh complete")
            self.log_success(logger, "Memory refresh complete")
            
        except Exception as e:
            print(f"🔴 [MEMORY] Memory refresh ERROR: {e}")
            self.log_error(logger, f"Memory refresh ERROR: {e}")
    
    async def display_mission_status(self):
        """Show current mission completion status."""
        print("🎯 [MEMORY] Displaying mission completion status...")
        self.log_info(logger, "Displaying mission completion status")
        
        if not self.connected:
            print("❌ [MEMORY] Not connected to game - cannot read mission status")
            self.log_error(logger, "Not connected to game - cannot read mission status")
            return
        
        try:
            # Read mission indices
            next_mission_idx = self.read_goal_address(next_mission_index_offset, sizeof_uint64)
            next_side_mission_idx = self.read_goal_address(next_side_mission_index_offset, sizeof_uint64)
            
            print(f"🎯 [MEMORY] === MISSION STATUS ===")
            print(f"🎯 [MEMORY] Main Missions Completed: {next_mission_idx}/70")
            print(f"🎯 [MEMORY] Side Missions Completed: {next_side_mission_idx}/24")
            print(f"🎯 [MEMORY] Total Locations Found: {len(self.location_outbox)}")
            print(f"🎯 [MEMORY] Game Finished: {self.finished_game}")
            
            if next_mission_idx > 0:
                print(f"🎯 [MEMORY] Completed main missions:")
                for i in range(int(next_mission_idx)):
                    raw_main_task_id = self.read_goal_address(missions_checked_offset + (i * sizeof_uint32),
                                                              sizeof_uint32)
                    if raw_main_task_id in main_tasks_to_missions:
                        mission = main_tasks_to_missions[raw_main_task_id]
                        print(f"🎯 [MEMORY]   {mission.id:2d}. {mission.name} (game-task: {raw_main_task_id})")
            
            if next_side_mission_idx > 0:
                print(f"🎯 [MEMORY] Completed side missions:")
                for i in range(int(next_side_mission_idx)):
                    raw_side_task_id = self.read_goal_address(side_missions_checked_offset + (i * sizeof_uint32),
                                                             sizeof_uint32)
                    if raw_side_task_id in side_tasks_to_missions:
                        side_mission = side_tasks_to_missions[raw_side_task_id]
                        print(f"🎯 [MEMORY]   {side_mission.id:2d}. {side_mission.name}")
            
            print(f"🎯 [MEMORY] === END MISSION STATUS ===")
            self.log_success(logger, "Mission status displayed successfully")
            
        except Exception as e:
            print(f"🔴 [MEMORY] Display mission status ERROR: {e}")
            self.log_error(logger, f"Display mission status ERROR: {e}")
    
    async def display_structure_info(self):
        """Display memory structure layout and offsets."""
        print("📋 [MEMORY] Displaying memory structure information...")
        self.log_info(logger, "Displaying memory structure information")
        
        print(f"📋 [MEMORY] === MEMORY STRUCTURE INFO ===")
        print(f"📋 [MEMORY] Expected version: {expected_memory_version}")
        print(f"📋 [MEMORY] Structure base address: {hex(self.goal_address) if self.goal_address else 'None'}")
        print(f"📋 [MEMORY] Marker address: {hex(self.marker_address) if self.marker_address else 'None'}")
        successful_marker_str = repr(self.successful_marker) if self.successful_marker else 'None'
        print(f"📋 [MEMORY] Successful marker: {successful_marker_str}")
        
        print(f"📋 [MEMORY] Structure offsets:")
        print(f"📋 [MEMORY]   Version: {memory_version_offset} (0x{memory_version_offset:x})")
        print(f"📋 [MEMORY]   Next mission index: {next_mission_index_offset} (0x{next_mission_index_offset:x})")
        print(f"📋 [MEMORY]   Next side mission index: {next_side_mission_index_offset} (0x{next_side_mission_index_offset:x})")
        print(f"📋 [MEMORY]   Missions array: {missions_checked_offset} (0x{missions_checked_offset:x})")
        print(f"📋 [MEMORY]   Side missions array: {side_missions_checked_offset} (0x{side_missions_checked_offset:x})")
        print(f"📋 [MEMORY]   Connection status: {connection_status_offset} (0x{connection_status_offset:x})")
        print(f"📋 [MEMORY]   End marker: {end_marker_offset} (0x{end_marker_offset:x})")
        print(f"📋 [MEMORY]   Total structure size: {offsets.current_offset} bytes")
        
        if self.connected and self.goal_address:
            try:
                version = self.read_goal_address(memory_version_offset, sizeof_uint32)
                print(f"📋 [MEMORY] Current version in memory: {version}")
                
                # Try to read connection status
                try:
                    connection_status = self.read_goal_address(connection_status_offset, sizeof_uint32)
                    status_names = {0: "disconnected", 1: "wait", 2: "ready", 3: "failure"}
                    status_name = status_names.get(connection_status, f"unknown({connection_status})")
                    print(f"📋 [MEMORY] Connection status: {connection_status} ({status_name})")
                except:
                    print(f"📋 [MEMORY] Connection status: Could not read")
                    
            except Exception as e:
                print(f"📋 [MEMORY] Could not read current values: {e}")
        
        print(f"📋 [MEMORY] === END STRUCTURE INFO ===")
        self.log_success(logger, "Structure info displayed successfully")
    
    def toggle_realtime_monitoring(self):
        """Toggle real-time monitoring of memory values."""
        self.realtime_monitoring = not self.realtime_monitoring
        
        if self.realtime_monitoring:
            print("📡 [MEMORY] Real-time monitoring ENABLED - memory values will be displayed continuously")
            self.log_success(logger, "Real-time monitoring enabled")
        else:
            print("🚫 [MEMORY] Real-time monitoring DISABLED")
            self.log_info(logger, "Real-time monitoring disabled")

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
                        logger.info(f"Mission completed! Raw game-task: {raw_main_task_id}"
                                    f" -> Mission ID: {main_mission_id}"
                                    f" -> '{mission_name}'")

                        if self.debug_enabled:
                            self.log_info(logger, f"[DEBUG] Completed mission translation:")
                            self.log_info(logger, f"  Raw game-task enum: {raw_main_task_id}")
                            self.log_info(logger, f"  Translated mission ID: {main_mission_id}")
                            self.log_info(logger, f"  Mission name: {mission_name}")

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
                        logger.info(f"Side mission completed! ID: {raw_side_task_id} -> '{side_mission_name}' "
                                    f"(location: {side_mission_id})")
                        
                        if self.debug_enabled:
                            self.log_info(logger, f"[DEBUG] Side mission completed:")
                            self.log_info(logger, f"  Side mission ID: {raw_side_task_id}")
                            self.log_info(logger, f"  Side mission name: {side_mission_name}")
                            self.log_info(logger, f"  Location ID added: {side_mission_id}")

            # Check if final boss is defeated (mission 65 - "Destroy Metal Kor at Nest")
            # Look for the raw game-task enum 70 which maps to mission 65
            completed_raw_missions = [self.read_goal_address(missions_checked_offset + (i * sizeof_uint32),
                                                             sizeof_uint32)
                                      for i in range(int(next_mission_idx))]
            
            if 70 in completed_raw_missions:  # game-task enum 70 = mission 65 "Destroy Metal Kor at Nest"
                if not self.finished_game:  # Only print once
                    self.finished_game = True
                    logger.info("Game completed! Final boss defeated (game-task enum 70 -> mission 65)")
                    if self.debug_enabled:
                        self.log_success(logger, "[DEBUG] Final boss defeated - game completion detected!")

        except (ProcessError, MemoryReadError, WinAPIError) as e:
            if self.debug_enabled:
                self.log_warn(logger, f"Memory read error during location scanning: {e}")
            else:
                logger.debug(f"Memory read error: {e}")
            return []

        return self.location_outbox

    def read_goal_address(self, offset: int, size: int) -> int:
        """Helper function to read from the GOAL memory structure at the given offset."""
        try:
            if self.debug_enabled or self.realtime_monitoring:
                print(f"🔍 [MEMORY] Reading {size} bytes at offset {offset} from 0x{self.goal_address + offset:x}")
            read_bytes = self.gk_process.read_bytes(self.goal_address + offset, size)
            if size == sizeof_uint64:
                return struct.unpack("<Q", read_bytes)[0]  # Little-endian uint64
            elif size == sizeof_uint32:
                return struct.unpack("<I", read_bytes)[0]  # Little-endian uint32
            elif size == sizeof_uint8:
                return struct.unpack("<B", read_bytes)[0]  # uint8
            else:
                raise ValueError(f"Unsupported size for reading: {size}")
        except (ProcessError, MemoryReadError, WinAPIError) as e:
            print(f"🔴 [MEMORY] Failed to read {size} bytes at offset {offset} from 0x{self.goal_address + offset:x}: {e}")
            if self.debug_enabled:
                logger.debug(f"Failed to read {size} bytes at offset {offset} from 0x{self.goal_address + offset:x}: {e}")
            else:
                logger.debug(f"Failed to read {size} bytes at offset {offset}: {e}")
            raise e
    
    def read_goal_address_safe(self, offset: int, size: int, default_value: int = 0) -> int:
        """Safe version that returns default value on error instead of raising exception."""
        try:
            return self.read_goal_address(offset, size)
        except Exception as e:
            if self.debug_enabled:
                logger.debug(f"Safe read failed at offset {offset}, size {size}: {e}")
            return default_value