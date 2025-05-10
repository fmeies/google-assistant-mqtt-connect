import unittest
from unittest.mock import patch, MagicMock
from src.data import update_data, data_cache

class TestData(unittest.TestCase):
    @patch("src.data.call_assistant")
    @patch("src.data.publish_to_mqtt")
    @patch("src.data.mqtt_config")
    @patch("src.data.server_config")
    def test_update_data(self, mock_server_config, mock_mqtt_config, mock_publish_to_mqtt, mock_call_assistant):
        """Test the update_data function."""
        # Mock configurations
        mock_mqtt_config.get.side_effect = lambda key, default: {
            "publish": {
                "key1": {
                    "command": "Test Command 1",
                    "regex": r"Result: (\d+)",
                    "result_map": {"1": "Success", "0": "Failure"}
                },
                "key2": {
                    "command": "Test Command 2",
                    "regex": r"Value: (\w+)",
                    "result_map": {}
                }
            }
        }.get(key, default)

        mock_server_config.get.return_value = 300

        # Mock call_assistant responses
        mock_call_assistant.side_effect = [
            "Result: 1",  # For key1
            "Value: TestValue"  # For key2
        ]

        # Call the function
        update_data()

        # Assert that call_assistant was called with the correct commands
        mock_call_assistant.assert_any_call("Test Command 1")
        mock_call_assistant.assert_any_call("Test Command 2")
        self.assertEqual(mock_call_assistant.call_count, 2)

        # Assert that data_cache was updated correctly
        self.assertEqual(data_cache["key1"], "Success")
        self.assertEqual(data_cache["key2"], "TestValue")
        self.assertIsNotNone(data_cache["timestamp"])
        self.assertIsNone(data_cache["error"])

        # Assert that publish_to_mqtt was called with the updated data_cache
        mock_publish_to_mqtt.assert_called_once_with(data_cache)

    @patch("src.data.call_assistant")
    @patch("src.data.logger")
    @patch("src.data.mqtt_config")
    def test_update_data_error_handling(self, mock_mqtt_config, mock_logger, mock_call_assistant):
        """Test error handling in update_data."""
        # Mock configurations
        mock_mqtt_config.get.side_effect = lambda key, default: {
            "publish": {
                "key1": {
                    "command": "Test Command 1",
                    "regex": r"Result: (\d+)",
                    "result_map": {}
                }
            }
        }.get(key, default)

        # Mock call_assistant to raise an exception
        mock_call_assistant.side_effect = Exception("Test error")

        # Call the function
        update_data()

        # Assert that the error was logged
        mock_logger.error.assert_called_once_with("Error updating status cache: Test error")

        # Assert that data_cache was updated with the error
        self.assertEqual(data_cache["error"], "Test error")
        self.assertIsNotNone(data_cache["timestamp"])
        self.assertIsNone(data_cache["key1"])

if __name__ == "__main__":
    unittest.main()