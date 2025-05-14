"""Unit tests for the DataUpdater class and its data update logic."""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from src.data import DataUpdater


class TestDataUpdater(unittest.TestCase):
    """Test cases for the DataUpdater class."""

    def test_update_data(self) -> None:
        """Test the update_data method."""
        # Mock assistant and MQTT configuration
        mock_assistant: MagicMock = MagicMock()
        mock_assistant.call_assistant.side_effect = ["Result: 1", "Value: TestValue"]

        mock_mqtt_config: Dict[str, Any] = {
            "publish": {
                "key1": {
                    "command": "Test Command 1",
                    "regex": r"Result: (\d+)",
                    "result_map": {"1": "Success", "0": "Failure"},
                },
                "key2": {
                    "command": "Test Command 2",
                    "regex": r"Value: (\w+)",
                    "result_map": {},
                },
            }
        }

        # Initialize DataUpdater
        data_updater: DataUpdater = DataUpdater(mock_assistant, mock_mqtt_config)

        # Call update_data
        data: Dict[str, Any] = data_updater.update_data()

        # Assert data cache updates
        self.assertEqual(data["key1"], "Success")
        self.assertEqual(data["key2"], "TestValue")
        self.assertIsNotNone(data["timestamp"])
        self.assertEqual(data["error"], "")

        # Assert assistant calls
        mock_assistant.call_assistant.assert_any_call("Test Command 1")
        mock_assistant.call_assistant.assert_any_call("Test Command 2")
        self.assertEqual(mock_assistant.call_assistant.call_count, 2)

    @patch("src.data.logger")
    def test_update_data_error_handling(self, mock_logger: MagicMock) -> None:
        """Test the update_data method."""
        # Mock call_assistant to raise an exception
        mock_assistant: MagicMock = MagicMock()
        mock_assistant.call_assistant.side_effect = RuntimeError("Test error")

        mock_mqtt_config: Dict[str, Any] = {
            "publish": {
                "key1": {
                    "command": "Test Command 1",
                    "regex": r"Result: (\d+)",
                    "result_map": {},
                }
            }
        }

        # Initialize DataUpdater
        data_updater: DataUpdater = DataUpdater(mock_assistant, mock_mqtt_config)

        # Call update_data
        data: Dict[str, Any] = data_updater.update_data()

        # Assert that the error was logged
        mock_logger.error.assert_called_once()

        # Assert that data_cache was updated with the error
        self.assertEqual(data["error"], "Test error")
        self.assertIsNotNone(data["timestamp"])
        self.assertIsNone(data["key1"])


if __name__ == "__main__":
    unittest.main()
