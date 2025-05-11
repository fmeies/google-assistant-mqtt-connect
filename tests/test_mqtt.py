import unittest
import json
from unittest.mock import patch, MagicMock
from src.mqtt import publish_to_mqtt, on_message


class TestMQTT(unittest.TestCase):
    @patch("src.mqtt.MQTT_CLIENT")
    def test_publish_to_mqtt(self, mock_mqtt_client):
        """Test the publish_to_mqtt function."""
        # Mock configurations
        mock_mqtt_config = {"publish": {"key1": "value1", "key2": "value2"}}
        data = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": 1672531200,  # Example timestamp
            "key1": "value1",
            "key2": "value2",
        }
        server_config = {"MQTT_TOPIC": "test/topic"}

        # Call the function
        publish_to_mqtt(server_config, mock_mqtt_config, data)

        # Assert that the MQTT client published the correct payload
        expected_payload = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": "2023-01-01 01:00:00",
            "key1": "value1",
            "key2": "value2",
        }
        mock_mqtt_client.publish.assert_called_once_with(
            "test/topic/stat", json.dumps(expected_payload)
        )

    @patch("src.mqtt.call_assistant")
    @patch("src.mqtt.logger")
    def test_on_message(self, mock_logger, mock_call_assistant):
        """Test the on_message function."""
        # Mock server and MQTT configurations
        mock_mqtt_config = {
            "subscribe": {"subtopic1": {"Command1": "Assistant Command 1"}}
        }

        # Mock MQTT message
        mock_message = MagicMock()
        mock_message.topic = "test/topic/cmnd/subtopic1"
        mock_message.payload.decode.return_value = "Command1"

        # Call the function
        on_message(None, mock_mqtt_config, mock_message)

        # Assert that the assistant command was called
        mock_call_assistant.assert_called_once_with("Assistant Command 1")

        # Test unsubscribed topic
        mock_message.topic = "test/topic/cmnd/unknown_subtopic"
        on_message(None, mock_mqtt_config, mock_message)
        mock_logger.warning.assert_called_with(
            "Received message on unsubscribed topic: %s", "unknown_subtopic"
        )

        # Test invalid command
        mock_message.topic = "test/topic/cmnd/subtopic1"
        mock_message.payload.decode.return_value = "InvalidCommand"
        on_message(None, mock_mqtt_config, mock_message)
        mock_logger.warning.assert_called_with(
            "Received command not in subscribed commands: %s", "InvalidCommand"
        )


if __name__ == "__main__":
    unittest.main()
