"""Unit tests for the MainApplication class and its update/publish logic."""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any, Dict
from parameterized import parameterized  # type: ignore

from src.main import MainApplication


class TestMainApplication(unittest.TestCase):
    """Test cases for MainApplication's update_and_publish_data method."""

    @parameterized.expand(
        [
            ("not_in_pause_hours", {"REQUEST_PAUSE_HOURS": [2, 3]}, 1, True),
            ("in_pause_hours", {"REQUEST_PAUSE_HOURS": [2, 3]}, 3, False),
            ("pause_hours_not_set", {}, 8, True),
            ("pause_hours_empty_array", {"REQUEST_PAUSE_HOURS": []}, 15, True),
        ]
    )
    def test_update_and_publish_data(
        self,
        _name: str,
        server_config: Dict[str, Any],
        current_hour: int,
        should_update: bool,
    ) -> None:
        """Test the update_and_publish_data method."""
        with patch("src.main.Config") as mock_config, patch(
            "src.main.GoogleAssistant"
        ) as _mock_google_assistant, patch(
            "src.main.DataUpdater"
        ) as mock_data_updater, patch(
            "src.main.MQTTClient"
        ) as mock_mqtt_client, patch(
            "src.main.time.localtime", return_value=MagicMock(tm_hour=current_hour)
        ):

            # Mock Config
            mock_config_instance = mock_config.return_value
            mock_config_instance.get_server_config.return_value = server_config
            mock_config_instance.get_mqtt_config.return_value = {}

            # Mock DataUpdater behavior
            mock_data_updater_instance = mock_data_updater.return_value
            mock_data_updater_instance.update_data.return_value = {"key": "value"}
            mock_data_updater_instance.data_cache = {"key": "cached_value"}

            # Mock MQTTClient behavior
            mock_mqtt_client_instance = mock_mqtt_client.return_value
            mock_mqtt_client_instance.publish_to_mqtt = MagicMock()

            # Initialize the application
            app = MainApplication()

            # Simulate the current hour
            app.update_and_publish_data()

            if should_update:
                mock_data_updater_instance.update_data.assert_called_once()
                mock_mqtt_client_instance.publish_to_mqtt.assert_called_once_with(
                    {"key": "value"}
                )
            else:
                mock_data_updater_instance.update_data.assert_not_called()
                mock_mqtt_client_instance.publish_to_mqtt.assert_called_once_with(
                    {"key": "cached_value"}
                )


if __name__ == "__main__":
    unittest.main()
