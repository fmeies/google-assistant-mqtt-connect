import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized
from src.main import main, update_and_publish_data


class TestMain(unittest.TestCase):
    @patch("src.main.init_config")
    @patch("src.main.init_mqtt_client")
    @patch("src.main.init_assistant")
    @patch("src.main.threading.Thread")
    def test_main(
        self, mock_thread, mock_init_assistant, mock_init_mqtt_client, mock_init_config
    ):
        """Test the main function."""
        # Mock init_config to return a tuple of server_config and mqtt_config
        mock_init_config.return_value = (
            {"MQTT_SERVER": "localhost"},  # server_config
            {"publish": {}},  # mqtt_config
        )

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

    @parameterized.expand(
        [
            # Test case 1: Current hour is not in pause hours
            ("not_in_pause_hours", {"REQUEST_PAUSE_HOURS": [2, 3]}, 1, True),
            # Test case 2: Current hour is in pause hours
            ("in_pause_hours", {"REQUEST_PAUSE_HOURS": [1]}, 1, False),
            # Test case 3: Pause hours not set
            ("pause_hours_not_set", {}, 1, True),
            # Test case 4: Pause hours empty array
            ("pause_hours_empty_array", {"REQUEST_PAUSE_HOURS": []}, 1, True),
        ]
    )
    @patch("src.main.update_data")
    @patch("src.main.publish_to_mqtt")
    @patch(
        "src.main.time.sleep", side_effect=KeyboardInterrupt
    )  # Simulate exiting the loop
    def test_update_and_publish_data(
        self,
        name,
        server_config,
        current_hour,
        should_update,
        mock_sleep,
        mock_publish_to_mqtt,
        mock_update_data,
    ):
        """Test the update_and_publish_data function with different configurations."""
        mqtt_config = {"publish": {}}

        # Mock update_data to return sample data
        mock_update_data.return_value = {"key": "value"}

        # Simulate the current hour
        with patch(
            "src.main.time.localtime", return_value=MagicMock(tm_hour=current_hour)
        ):
            with self.assertRaises(KeyboardInterrupt):  # Exit the infinite loop
                update_and_publish_data(server_config, mqtt_config)

        if should_update:
            # Assert that update_data and publish_to_mqtt were called
            mock_update_data.assert_called_once_with(mqtt_config)
            mock_publish_to_mqtt.assert_called_once_with(
                server_config, mqtt_config, {"key": "value"}
            )
        else:
            # Assert that update_data and publish_to_mqtt were NOT called
            mock_update_data.assert_not_called()
            mock_publish_to_mqtt.assert_not_called()


if __name__ == "__main__":
    unittest.main()
