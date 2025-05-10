import unittest
from unittest.mock import patch
from src.main import main

class TestMain(unittest.TestCase):
    @patch("src.main.init_config")
    @patch("src.main.init_mqtt_client")
    @patch("src.main.init_assistant")
    @patch("src.main.data_updater")
    @patch("src.main.threading.Thread")
    def test_main(self, mock_thread, mock_data_updater, mock_init_assistant, mock_init_mqtt_client, mock_init_config):
        """Test the main function."""
        mock_thread.return_value.start = lambda: None
        with patch("src.main.time.sleep", side_effect=KeyboardInterrupt):
            main()
        mock_init_config.assert_called_once()
        mock_init_mqtt_client.assert_called_once()
        mock_init_assistant.assert_called_once()
        mock_thread.assert_called_once()

if __name__ == "__main__":
    unittest.main()