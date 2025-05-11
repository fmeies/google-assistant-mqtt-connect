import unittest
from unittest.mock import patch, MagicMock
from src.data import update_data

class TestData(unittest.TestCase):
    @patch("src.data.call_assistant")
    def test_update_data(self, mock_call_assistant):
        """Test the update_data function."""
        # Mock configurations
        mock_mqtt_config = {
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
        }

        # Mock call_assistant responses
        mock_call_assistant.side_effect = [
            "Result: 1",  # For key1
            "Value: TestValue"  # For key2
        ]

        # Call the function
        data = update_data(mock_mqtt_config) 

        # Assert that call_assistant was called with the correct commands
        mock_call_assistant.assert_any_call("Test Command 1")
        mock_call_assistant.assert_any_call("Test Command 2")
        self.assertEqual(mock_call_assistant.call_count, 2)

        # Assert that data was updated correctly
        self.assertEqual(data["key1"], "Success")
        self.assertEqual(data["key2"], "TestValue")
        self.assertIsNotNone(data["timestamp"])
        self.assertEqual(data["error"], "")

    @patch("src.data.call_assistant")
    @patch("src.data.logger")
    def test_update_data_error_handling(self, mock_logger, mock_call_assistant):
        """Test error handling in update_data."""
        # Mock configurations
        mock_mqtt_config = {
            "publish": {
                "key1": {
                    "command": "Test Command 1",
                    "regex": r"Result: (\d+)",
                    "result_map": {}
                }
            }
        }

        # Mock call_assistant to raise an exception
        mock_call_assistant.side_effect = Exception("Test error")

        # Call the function
        data = update_data(mock_mqtt_config)

        # Assert that the error was logged
        mock_logger.error.assert_called_once_with("Error updating status cache: Test error")

        # Assert that data_cache was updated with the error
        self.assertEqual(data["error"], "Test error")
        self.assertIsNotNone(data["timestamp"])
        self.assertIsNone(data["key1"])

if __name__ == "__main__":
    unittest.main()