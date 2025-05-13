import unittest
import json
from unittest.mock import patch, MagicMock
from src.mqtt import MQTTClient


class TestMQTTClient(unittest.TestCase):
    @patch("paho.mqtt.client.Client")  # Fixed the import path
    def test_publish_to_mqtt(self, mock_paho_client):
        """Test the publish_to_mqtt method."""
        # Mock configurations
        mock_assistant = MagicMock()
        mock_server_config = {
            "MQTT_TOPIC": "test/topic",
            "MQTT_CLIENT_ID": "test_id",
            "MQTT_SERVER": "localhost",
            "MQTT_PORT": 1883,
        }
        mock_mqtt_config = {"publish": {"key1": "value1", "key2": "value2"}}
        data = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": 1672531200,  # Example timestamp
            "key1": "value1",
            "key2": "value2",
        }

        # Initialize MQTTClient
        mqtt_client = MQTTClient(mock_assistant, mock_server_config, mock_mqtt_config)

        # Call the publish_to_mqtt method
        mqtt_client.publish_to_mqtt(data)

        # Assert that the MQTT client published the correct payload
        expected_payload = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": "2023-01-01 01:00:00",
            "key1": "value1",
            "key2": "value2",
        }
        mock_paho_client.return_value.publish.assert_called_once_with(
            "test/topic/stat", json.dumps(expected_payload)
        )

    @patch("src.mqtt.logger")  # Mock the module-level logger
    @patch("paho.mqtt.client.Client")
    def test_on_message(self, _mock_paho_client, mock_logger):
        """Test the on_message method."""
        # Mock configurations
        mock_assistant = MagicMock()
        mock_server_config = {
            "MQTT_TOPIC": "test/topic",
            "MQTT_CLIENT_ID": "test_id",
            "MQTT_SERVER": "localhost",
            "MQTT_PORT": 1883,
        }
        mock_mqtt_config = {
            "subscribe": {"subtopic1": {"Command1": "Assistant Command 1"}}
        }

        # Initialize MQTTClient
        mqtt_client = MQTTClient(mock_assistant, mock_server_config, mock_mqtt_config)

        # Mock MQTT message
        mock_message = MagicMock()
        mock_message.topic = "test/topic/cmnd/subtopic1"
        mock_message.payload.decode.return_value = "Command1"

        # Call the on_message method
        mqtt_client.on_message(
            None,
            {"assistant": mock_assistant, "mqtt_config": mock_mqtt_config},
            mock_message,
        )

        # Assert that the assistant command was called
        mock_assistant.call_assistant.assert_called_once_with("Assistant Command 1")

        # Test unsubscribed topic
        mock_message.topic = "test/topic/cmnd/unknown_subtopic"
        mqtt_client.on_message(
            None,
            {"assistant": mock_assistant, "mqtt_config": mock_mqtt_config},
            mock_message,
        )
        mock_logger.warning.assert_any_call(
            "Received message on unsubscribed topic: %s", "unknown_subtopic"
        )

        # Test invalid command
        mock_message.topic = "test/topic/cmnd/subtopic1"
        mock_message.payload.decode.return_value = "InvalidCommand"
        mqtt_client.on_message(
            None,
            {"assistant": mock_assistant, "mqtt_config": mock_mqtt_config},
            mock_message,
        )
        mock_logger.warning.assert_any_call(
            "Received command not in subscribed commands: %s", "InvalidCommand"
        )


if __name__ == "__main__":
    unittest.main()
