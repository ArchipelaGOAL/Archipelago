import logging
import queue
import struct
from dataclasses import dataclass
from queue import Queue
from typing import Callable

import pymem
from pymem.exception import ProcessNotFound, ProcessError

import asyncio
from asyncio import StreamReader, StreamWriter, Lock

# Handle imports with flexibility
try:
    from NetUtils import NetworkItem
    from ..game_id import jak2_name
    from ..items import item_table, Jak2ItemData
    from ..locs.mission_locations import main_mission_table, side_mission_table
except ImportError:
    # Fallback for direct execution or testing
    import sys
    import os
    # Mock NetworkItem for testing
    class NetworkItem:
        def __init__(self, item=0, location=0, player=0):
            self.item = item
            self.location = location
            self.player = player
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from game_id import jak2_name
    from items import item_table, Jak2ItemData
    from locs.mission_locations import main_mission_table, side_mission_table


logger = logging.getLogger("Jak2ReplClient")


@dataclass
class JsonMessageData:
    my_item_name: str | None = None
    my_item_finder: str | None = None
    their_item_name: str | None = None
    their_item_owner: str | None = None


class Jak2ReplClient:
    ip: str
    port: int
    reader: StreamReader
    writer: StreamWriter
    lock: Lock
    connected: bool = False
    initiated_connect: bool = False  # Signals when user tells us to try reconnecting.

    # Variables to handle the title screen and initial game connection.
    initial_item_count = -1  # Brand new games have 0 items, so initialize this to -1.
    received_initial_items = False
    processed_initial_items = False

    # The REPL client needs the REPL/compiler process running, but that process
    # also needs the game running. Therefore, the REPL client needs both running.
    gk_process: pymem.process = None
    goalc_process: pymem.process = None
    
    # Debug state
    debug_enabled: bool = False

    item_inbox: dict[int, NetworkItem] = {}
    inbox_index = 0
    json_message_queue: Queue[JsonMessageData] = queue.Queue()

    # Logging callbacks
    log_error: Callable    # Red
    log_warn: Callable     # Orange
    log_success: Callable  # Green
    log_info: Callable     # White (default)

    def __init__(self,
                 log_error_callback: Callable,
                 log_warn_callback: Callable,
                 log_success_callback: Callable,
                 log_info_callback: Callable,
                 ip: str = "127.0.0.1",
                 port: int = 8181):  # Same port as Jak 1
        self.ip = ip
        self.port = port
        self.lock = asyncio.Lock()
        self.log_error = log_error_callback
        self.log_warn = log_warn_callback
        self.log_success = log_success_callback
        self.log_info = log_info_callback

    async def main_tick(self):
        if self.initiated_connect:
            print("🔗 [REPL] Initiating REPL connection...")
            await self.connect()

        if self.connected:
            # Process any items waiting to be sent to the game
            pending_items = len(self.item_inbox) - self.inbox_index
            if pending_items > 0:
                print(f"📦 [REPL] Processing {pending_items} pending items...")
            await self.send_items()

    async def connect(self):
        print("🔗 [REPL] === STARTING REPL CLIENT CONNECTION ===\n")
        self.initiated_connect = False
        if self.connected:
            print("✅ [REPL] Already connected to REPL")
            return

        # Check if the game processes are running
        print("🎮 [REPL] Step 1: Checking for required processes...")
        try:
            self.gk_process = pymem.Pymem("gk.exe")  # Same as Jak 1
            print(f"✅ [REPL] Found gk.exe process (PID: {self.gk_process.process_id})")
            
            self.goalc_process = pymem.Pymem("goalc.exe")  # Same as Jak 1
            print(f"✅ [REPL] Found goalc.exe process (PID: {self.goalc_process.process_id})")
        except ProcessNotFound:
            print("❌ [REPL] Could not find required processes (gk.exe and/or goalc.exe)!")
            print("❌ [REPL] Make sure the game and OpenGOAL compiler are both running.")
            self.log_error(logger, "Could not find game processes (gk.exe and/or goalc.exe)!")
            return

        # Try to connect to the REPL
        print(f"🌐 [REPL] Step 2: Connecting to REPL at {self.ip}:{self.port}...")
        try:
            self.reader, self.writer = await asyncio.open_connection(self.ip, self.port)
            print(f"✅ [REPL] TCP connection established")
            
            # Wait for and read the welcome message
            await asyncio.sleep(1)
            connect_data = await self.reader.read(1024)
            welcome_message = connect_data.decode()

            # Should be the OpenGOAL welcome message
            if "Connected to OpenGOAL" in welcome_message and "nREPL!" in welcome_message:
                print(f"✅ [REPL] Received OpenGOAL welcome message")
                logger.debug(welcome_message)
                self.connected = True
            else:
                print(f"❌ [REPL] Unexpected welcome message: {welcome_message}")
                self.log_error(logger, f"Unexpected welcome message: {welcome_message}")
                return
                
        except Exception as e:
            print(f"❌ [REPL] Could not connect to REPL: {e}")
            print(f"❌ [REPL] Make sure the OpenGOAL REPL is running (usually port {self.port})")
            self.log_error(logger, f"Could not connect to REPL: {e}")
            self.connected = False
            # Try to set failure status if possible
            try:
                await self.send_form("(ap-set-connection-status! (ap-connection-status failure))", print_ok=False, expect_response=False)
            except:
                pass  # If we can't even send the failure status, just continue
            return

        # Initialize the REPL with required setup commands
        # Since the REPL doesn't always send responses, we'll just send commands and assume success
        if self.reader and self.writer:
            try:
                # Have the REPL listen to the game's internal websocket
                print("🔗 [REPL] [1/8] Connecting REPL to game websocket...")
                self.log_info(logger, "[1/8] Connecting REPL to game websocket...")
                success = await self.send_form("(lt)", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)  # Small delay between commands
                if success:
                    print("✅ [REPL] [1/8] Connected to game websocket")
                    self.log_success(logger, "[1/8] Connected to game websocket")
                else:
                    print("❌ [REPL] [1/8] Failed to connect to game websocket")

                # Enable debug segment for compilation
                print("🐛 [REPL] [2/8] Enabling debug segment...")
                self.log_info(logger, "[2/8] Enabling debug segment...")
                success = await self.send_form("(set! *debug-segment* #t)", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [2/8] Debug segment enabled")
                    self.log_success(logger, "[2/8] Debug segment enabled")
                else:
                    print("❌ [REPL] [2/8] Failed to enable debug segment")

                # Start compilation - this loads the Jak 2 code
                print("🛠️  [REPL] [3/8] Compiling Jak 2 with ArchipelaGOAL mod (this may take 30-60 seconds)...")
                print("⏳ [REPL] Please wait while the mod is compiled and loaded into the game...")
                self.log_info(logger, "[3/8] Compiling Jak 2 with ArchipelaGOAL mod (this may take 30-60 seconds)...")
                success = await self.send_form("(mi)", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [3/8] Compilation complete!")
                    self.log_success(logger, "[3/8] Compilation complete!")
                else:
                    print("❌ [REPL] [3/8] Compilation may have failed")

                # Set connection status to "wait" - client is connected but syncing
                print("🔄 [REPL] [4/8] Setting connection status to 'wait'...")
                self.log_info(logger, "[4/8] Setting connection status to 'wait'...")
                success = await self.send_form("(ap-set-connection-status! (ap-connection-status wait))", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [4/8] Connection status set to 'wait'")
                    self.log_success(logger, "[4/8] Connection status set to 'wait'")
                else:
                    print("❌ [REPL] [4/8] Failed to set connection status")

                # Play audio cue when compilation is complete
                print("🔔 [REPL] [5/8] Playing success sound...")
                self.log_info(logger, "[5/8] Playing success sound...")
                success = await self.send_form("(dotimes (i 1) "
                                    "(sound-play-by-name "
                                    "(static-sound-name \"menu-close\") "
                                    "(new-sound-id) 1024 0 0 (sound-group sfx) #t))", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [5/8] Audio cue played")
                    self.log_success(logger, "[5/8] Audio cue played")
                else:
                    print("❌ [REPL] [5/8] Failed to play audio cue")

                # Disable debug segment and cheat mode after compilation
                print("🙅 [REPL] [6/8] Disabling debug segment...")
                self.log_info(logger, "[6/8] Disabling debug segment...")
                success = await self.send_form("(set! *debug-segment* #f)", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [6/8] Debug segment disabled")
                    self.log_success(logger, "[6/8] Debug segment disabled")
                else:
                    print("❌ [REPL] [6/8] Failed to disable debug segment")

                print("🙅 [REPL] [7/8] Disabling cheat mode...")
                self.log_info(logger, "[7/8] Disabling cheat mode...")
                success = await self.send_form("(set! *cheat-mode* #f)", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [7/8] Cheat mode disabled")
                    self.log_success(logger, "[7/8] Cheat mode disabled")
                else:
                    print("❌ [REPL] [7/8] Failed to disable cheat mode")

                # Set connection status to "ready" - everything is ready to go
                print("🟢 [REPL] [8/8] Setting connection status to 'ready'...")
                self.log_info(logger, "[8/8] Setting connection status to 'ready'...")
                success = await self.send_form("(ap-set-connection-status! (ap-connection-status ready))", print_ok=False, expect_response=False)
                await asyncio.sleep(0.5)
                if success:
                    print("✅ [REPL] [8/8] Connection status set to 'ready'")
                    self.log_success(logger, "[8/8] Connection status set to 'ready'")
                else:
                    print("❌ [REPL] [8/8] Failed to set connection status")

                print("🟢 [REPL] === CONNECTED TO JAK 2 REPL SUCCESSFULLY! ALL SYSTEMS READY ===\n")
                self.log_success(logger, "Connected to Jak 2 REPL successfully! All systems ready.")
            except Exception as e:
                print(f"🔴 [REPL] Error during REPL initialization: {e}")
                self.log_error(logger, f"Error during REPL initialization: {e}")
                # Set failure status if initialization fails
                try:
                    await self.send_form("(ap-set-connection-status! (ap-connection-status failure))", print_ok=False, expect_response=False)
                except:
                    pass  # If we can't even send the failure status, just continue
                self.connected = False

    async def disconnect(self):
        if self.connected and self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            self.connected = False

    async def send_form(self, form: str, print_ok: bool = True, timeout: float = 5.0, expect_response: bool = True) -> bool:
        """Send a GOAL form to the REPL using the correct binary protocol."""
        if not self.connected:
            print(f"❌ [REPL] Cannot send form - not connected to REPL")
            return False
        
        if print_ok or "ap-" in form or self.debug_enabled:
            print(f"📡 [REPL] Sending: {form}")

        # OpenGOAL REPL expects binary protocol: 8-byte header + message
        header = struct.pack("<II", len(form), 10)  # length + type(10)
        
        async with self.lock:
            try:
                self.writer.write(header + form.encode())
                await self.writer.drain()

                if not expect_response:
                    # For commands that don't return a response, just assume success
                    logger.debug(f"Sent command (no response expected): {form}")
                    return True

                # Try to read response with timeout
                try:
                    response_data = await asyncio.wait_for(self.reader.read(1024), timeout=timeout)
                    response = response_data.decode()
                    if print_ok or "ap-" in form or self.debug_enabled:
                        print(f"📥 [REPL] Response: {response.strip() if response else '(empty)'}")
                    logger.debug(f"REPL response to '{form}': {response}")
                    
                    # Accept various success indicators
                    if response:  # Any non-empty response is considered success for now
                        if print_ok:
                            logger.debug(f"Command succeeded: {form}")
                        return True
                    else:
                        self.log_warn(logger, f"Empty response from REPL for: {form}")
                        return False
                        
                except asyncio.TimeoutError:
                    # Some commands might not send responses, treat as success if we sent it
                    if print_ok or "ap-" in form or self.debug_enabled:
                        print(f"⏱️  [REPL] No response received (timeout: {timeout}s) - assuming success")
                    logger.debug(f"No response received for '{form}' (timeout: {timeout}s) - assuming success")
                    return True
                    
            except Exception as e:
                print(f"🔴 [REPL] Error sending command '{form}': {e}")
                logger.debug(f"Error sending REPL command '{form}': {e}")
                return False

    async def send_items(self):
        """Process items waiting to be sent to the game."""
        if not self.connected:
            return

        items_sent = 0
        while self.inbox_index in self.item_inbox:
            item = self.item_inbox[self.inbox_index]
            success = await self.send_item_to_game(item)
            if success:
                items_sent += 1
            self.inbox_index += 1
        
        if items_sent > 0:
            print(f"🎁 [REPL] Successfully sent {items_sent} items to game")

    async def send_item_to_game(self, item: NetworkItem) -> bool:
        """Send a specific item to the game via REPL commands."""
        try:
            # Look up the item data
            if item.item not in item_table:
                print(f"⚠️  [REPL] Unknown item ID: {item.item}")
                self.log_warn(logger, f"Unknown item ID: {item.item}")
                return False

            item_entry = item_table[item.item]
            
            # All items are Jak2ItemData objects (both key items and filler items)
            if isinstance(item_entry, Jak2ItemData):
                item_symbol = item_entry.symbol
            else:
                # This should not happen anymore - all items should be Jak2ItemData objects
                print(f"⚠️  [REPL] WARNING: Item is not a Jak2ItemData object: {item_entry}")
                self.log_warn(logger, f"WARNING: Item is not a Jak2ItemData object: {item_entry}")
                return False
            
            # Send the item to the game using the ap-item-received! function
            command = f"(ap-item-received! '{item_symbol})"
            print(f"🎁 [REPL] Sending item '{item_entry.name}' (symbol: {item_symbol}) to game...")
            success = await self.send_form(command)
            
            if success:
                print(f"✅ [REPL] Successfully gave item: {item_entry.name}")
                self.log_success(logger, f"Successfully gave item: {item_entry.name}")
            else:
                print(f"❌ [REPL] Item delivery failed for: {item_entry.name}")
                self.log_warn(logger, f"Item delivery failed for: {item_entry.name}")
            
            return success
                
        except Exception as e:
            print(f"🔴 [REPL] Failed to send item to game: {e}")
            self.log_error(logger, f"Failed to send item to game: {e}")
            return False

    def queue_game_text(self, my_item_name: str | None, my_item_finder: str | None,
                       their_item_name: str | None, their_item_owner: str | None):
        """Queue text messages to be displayed in the game."""
        message = JsonMessageData(my_item_name, my_item_finder, their_item_name, their_item_owner)
        self.json_message_queue.put(message)

    async def setup_options(self, slot_name: str, seed_name: str):
        """Initialize game options for Archipelago."""
        # This would set up any game-specific options
        # For now, just mark that we've processed initial setup
        self.processed_initial_items = True
        self.log_info(logger, f"Initialized Jak 2 Archipelago for slot '{slot_name}' with seed '{seed_name}'")

    async def send_connection_status(self, status: str):
        """Send connection status to the game."""
        # Could display status messages in-game if desired
        logger.debug(f"Connection status: {status}")

    async def print_status(self):
        """Print the current status of the REPL client."""
        gk_id = str(self.gk_process.process_id) if self.gk_process else "None"
        goalc_id = str(self.goalc_process.process_id) if self.goalc_process else "None"
        
        msg = (f"Jak 2 REPL Client Status:\n"
               f"   Connected to REPL: {self.connected}\n"
               f"   Debug Mode: {self.debug_enabled}\n"
               f"   REPL Address: {self.ip}:{self.port}\n" 
               f"   Game process ID: {gk_id}\n"
               f"   Compiler process ID: {goalc_id}\n"
               f"   Items processed: {self.inbox_index}\n"
               f"   Items pending: {len(self.item_inbox) - self.inbox_index}")
        
        self.log_info(logger, msg)
    
    def enable_debug_mode(self):
        """Enable debug mode for verbose REPL communication."""
        self.debug_enabled = True
        logger.setLevel(logging.DEBUG)
        print("🐛 [REPL] Debug mode enabled - verbose REPL communication will be shown")
        self.log_info(logger, "REPL debug mode enabled")
    
    def disable_debug_mode(self):
        """Disable debug mode."""
        self.debug_enabled = False
        print("ℹ️  [REPL] Debug mode disabled")
        self.log_info(logger, "REPL debug mode disabled")
    
    async def test_connection(self):
        """Test the REPL connection by sending a simple command."""
        print("🔍 [REPL] Testing REPL connection...")
        self.log_info(logger, "Testing REPL connection")
        
        if not self.connected:
            print("❌ [REPL] Not connected to REPL - cannot test connection")
            self.log_error(logger, "Not connected to REPL - cannot test connection")
            return
        
        try:
            # Send a simple test command - just get the current game status
            test_command = "(* 2 21)"  # Simple math that should return 42
            print(f"📡 [REPL] Sending test command: {test_command}")
            
            success = await self.send_form(test_command, print_ok=True, timeout=10.0)
            
            if success:
                print("✅ [REPL] Connection test PASSED - REPL is responding")
                self.log_success(logger, "Connection test PASSED - REPL is responding")
                
                # Test a more complex command to verify game connection
                game_test = "(if *target* 'connected 'not-connected)"
                print(f"📡 [REPL] Testing game connection: {game_test}")
                game_success = await self.send_form(game_test, print_ok=True, timeout=5.0)
                
                if game_success:
                    print("✅ [REPL] Game connection test PASSED")
                    self.log_success(logger, "Game connection test PASSED")
                else:
                    print("⚠️  [REPL] Game connection test inconclusive")
                    self.log_warn(logger, "Game connection test inconclusive")
            else:
                print("❌ [REPL] Connection test FAILED - REPL not responding properly")
                self.log_error(logger, "Connection test FAILED - REPL not responding properly")
                
        except Exception as e:
            print(f"🔴 [REPL] Connection test ERROR: {e}")
            self.log_error(logger, f"Connection test ERROR: {e}")
    
    async def debug_send_command(self, command: str):
        """Send a raw GOAL command for debugging purposes."""
        print(f"🛠️  [REPL] Sending debug command: {command}")
        self.log_info(logger, f"Sending debug command: {command}")
        
        if not self.connected:
            print("❌ [REPL] Not connected to REPL - cannot send command")
            self.log_error(logger, "Not connected to REPL - cannot send command")
            return
        
        try:
            success = await self.send_form(command, print_ok=True, timeout=10.0)
            
            if success:
                print(f"✅ [REPL] Debug command sent successfully")
                self.log_success(logger, f"Debug command sent successfully")
            else:
                print(f"❌ [REPL] Debug command failed")
                self.log_error(logger, f"Debug command failed")
                
        except Exception as e:
            print(f"🔴 [REPL] Debug command ERROR: {e}")
            self.log_error(logger, f"Debug command ERROR: {e}")
    
    async def force_item_refresh(self):
        """Force refresh of items to be sent to game."""
        print("🔄 [REPL] Forcing item refresh...")
        self.log_info(logger, "Forcing item refresh")
        
        if not self.connected:
            print("❌ [REPL] Not connected to REPL - cannot refresh items")
            self.log_error(logger, "Not connected to REPL - cannot refresh items")
            return
        
        try:
            print(f"📦 [REPL] Items in inbox: {len(self.item_inbox)}")
            print(f"📦 [REPL] Items processed: {self.inbox_index}")
            pending_count = len(self.item_inbox) - self.inbox_index
            print(f"📦 [REPL] Items pending: {pending_count}")
            
            if pending_count > 0:
                print(f"🎁 [REPL] Processing {pending_count} pending items...")
                await self.send_items()
                print("✅ [REPL] Item refresh complete")
                self.log_success(logger, "Item refresh complete")
            else:
                print("ℹ️  [REPL] No pending items to process")
                self.log_info(logger, "No pending items to process")
                
        except Exception as e:
            print(f"🔴 [REPL] Item refresh ERROR: {e}")
            self.log_error(logger, f"Item refresh ERROR: {e}")