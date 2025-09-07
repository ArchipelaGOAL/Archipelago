import unittest
from unittest.mock import patch, MagicMock

class TestJak2Client(unittest.TestCase):
    """Test basic functionality of the Jak 2 client."""
    
    def test_client_import(self):
        """Test that the client module can be imported successfully."""
        try:
            from worlds.jakii import client
            self.assertTrue(hasattr(client, 'launch'))
            self.assertTrue(hasattr(client, 'Jak2Context'))
        except ImportError as e:
            self.fail(f"Failed to import Jak 2 client: {e}")
    
    def test_agents_import(self):
        """Test that agent modules can be imported successfully."""
        try:
            from worlds.jakii.agents.memory_reader import Jak2MemoryReader
            from worlds.jakii.agents.repl_client import Jak2ReplClient
            self.assertTrue(Jak2MemoryReader)
            self.assertTrue(Jak2ReplClient)
        except ImportError as e:
            self.fail(f"Failed to import Jak 2 agents: {e}")

    @patch('pymem.Pymem')
    def test_memory_reader_creation(self, mock_pymem):
        """Test that the memory reader can be created."""
        from worlds.jakii.agents.memory_reader import Jak2MemoryReader
        
        # Mock callbacks
        location_callback = MagicMock()
        finish_callback = MagicMock()
        error_callback = MagicMock()
        warn_callback = MagicMock()
        success_callback = MagicMock()
        info_callback = MagicMock()
        
        reader = Jak2MemoryReader(
            location_callback,
            finish_callback,
            error_callback,
            warn_callback,
            success_callback,
            info_callback
        )
        
        self.assertFalse(reader.connected)
        self.assertFalse(reader.initiated_connect)
        
    def test_repl_client_creation(self):
        """Test that the REPL client can be created."""
        from worlds.jakii.agents.repl_client import Jak2ReplClient
        
        # Mock callbacks
        error_callback = MagicMock()
        warn_callback = MagicMock()
        success_callback = MagicMock()
        info_callback = MagicMock()
        
        repl = Jak2ReplClient(
            error_callback,
            warn_callback,
            success_callback,
            info_callback
        )
        
        self.assertFalse(repl.connected)
        self.assertFalse(repl.initiated_connect)
        self.assertEqual(repl.ip, "127.0.0.1")
        self.assertEqual(repl.port, 8181)


if __name__ == '__main__':
    unittest.main()