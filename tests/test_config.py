import unittest
from src.config import init_config

class TestConfig(unittest.TestCase):
    def test_init_config(self):
        """Test the init_config function."""
        self.assertIsNone(init_config())

if __name__ == "__main__":
    unittest.main()