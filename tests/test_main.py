import unittest
from unittest.mock import patch, MagicMock
from src.main import main

class TestMain(unittest.TestCase):
    @patch("src.main.init_config")
    @patch("src.main.init_mqtt_client")
    @patch("src.main.init_assistant")
    @patch("src.main.threading.Thread")
    def test_main(self, mock_thread, mock_init_assistant, mock_init_mqtt_client, mock_init_config):
        """Test the main function."""
        # Mock init_config to return a tuple of server_config and mqtt_config
        mock_init_config.return_value = ({"MQTT_SERVER": "localhost"}, {"publish": {}})

        # Mock the thread's start method
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        # Simulate a KeyboardInterrupt to exit the infinite loop in main
        with patch("src.main.time.sleep", side_effect=KeyboardInterrupt):
            main()

        # Assert that the initialization functions were called once
        mock_init_config.assert_called_once()
        mock_init_mqtt_client.assert_called_once()
        mock_init_assistant.assert_called_once()

        # Assert that the thread was started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

if __name__ == "__main__":
    unittest.main()