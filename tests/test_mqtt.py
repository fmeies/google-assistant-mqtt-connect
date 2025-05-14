"""Unit tests for the MQTTClient class and MQTT message handling."""

import unittest
import json
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from src.mqtt import MQTTClient


class TestMQTTClient(unittest.TestCase):
    """Test cases for the MQTTClient class."""

    @patch("paho.mqtt.client.Client")
    def test_publish_to_mqtt(self, mock_paho_client: MagicMock) -> None:
        """Test the publish_to_mqtt method."""
        # Mock configurations
        mock_assistant: MagicMock = MagicMock()
        mock_server_config: Dict[str, Any] = {
            "MQTT_TOPIC": "test/topic",
            "MQTT_CLIENT_ID": "test_id",
            "MQTT_SERVER": "localhost",
            "MQTT_PORT": 1883,
        }
        mock_mqtt_config: Dict[str, Any] = {
            "publish": {"key1": "value1", "key2": "value2"}
        }

        some_timestamp = 1672531200
        data: Dict[str, Any] = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": some_timestamp,
            "key1": "value1",
            "key2": "value2",
        }

        # Initialize MQTTClient
        mqtt_client: MQTTClient = MQTTClient(
            mock_assistant, mock_server_config, mock_mqtt_config
        )

        # Call the publish_to_mqtt method
        mqtt_client.publish_to_mqtt(data)

        # Assert that the MQTT client published the correct payload
        expected_payload: Dict[str, Any] = {
            "sdk_calls_today": 5,
            "error": "",
            "timestamp": MQTTClient.format_date(some_timestamp),
            "key1": "value1",
            "key2": "value2",
        }
        mock_paho_client.return_value.publish.assert_called_once_with(
            "test/topic/stat", json.dumps(expected_payload)
        )

    @patch("src.mqtt.logger")
    @patch("paho.mqtt.client.Client")
    def test_on_message(
        self, _mock_paho_client: MagicMock, mock_logger: MagicMock
    ) -> None:
        """Test the on_message method."""
        # Mock configurations
        mock_assistant: MagicMock = MagicMock()
        mock_server_config: Dict[str, Any] = {
            "MQTT_TOPIC": "test/topic",
            "MQTT_CLIENT_ID": "test_id",
            "MQTT_SERVER": "localhost",
            "MQTT_PORT": 1883,
        }
        mock_mqtt_config: Dict[str, Any] = {
            "subscribe": {"subtopic1": {"Command1": "Assistant Command 1"}}
        }

        # Initialize MQTTClient
        mqtt_client: MQTTClient = MQTTClient(
            mock_assistant, mock_server_config, mock_mqtt_config
        )

        # Mock MQTT message
        mock_message: MagicMock = MagicMock()
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
