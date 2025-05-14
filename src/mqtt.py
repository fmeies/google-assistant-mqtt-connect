"""
This module provides functionality to interact with an MQTT broker.
"""

import logging
import datetime
import json
from typing import Any, Dict
import paho.mqtt.client as pahomqtt # pylint: disable=import-error

from src.assistant import GoogleAssistant

logger = logging.getLogger(__name__)


class MQTTClient:
    """Encapsulates the MQTT client logic."""

    assistant: GoogleAssistant
    server_config: Dict[str, Any]
    mqtt_config: Dict[str, Any]
    client: pahomqtt.Client

    def __init__(
        self,
        assistant: GoogleAssistant,
        server_config: Dict[str, Any],
        mqtt_config: Dict[str, Any],
    ) -> None:
        self.assistant = assistant
        self.server_config = server_config
        self.mqtt_config = mqtt_config
        self.client = pahomqtt.Client(protocol=pahomqtt.MQTTv311)

        # Initialize the MQTT client during object creation
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Set up and initialize the MQTT client."""
        client_id = self.server_config["MQTT_CLIENT_ID"]
        server = self.server_config["MQTT_SERVER"]
        port = self.server_config["MQTT_PORT"]
        topic = self.server_config["MQTT_TOPIC"]
        user_name = self.server_config.get("MQTT_USERNAME")
        password = self.server_config.get("MQTT_PASSWORD")

        if user_name and password:
            self.client.username_pw_set(user_name, password)
        self.client.user_data_set(client_id)
        self.client.on_message = self.on_message
        self.client.reconnect_delay_set(min_delay=1, max_delay=120)
        self.client.connect(server, port, 60)
        logger.info("Subscribing to topic: %s/cmnd/#", topic)
        self.client.subscribe(f"{topic}/cmnd/#")
        self.client.loop_start()

    def on_message(self, _client, _userdata, message) -> None:
        """Callback function to handle incoming messages."""
        # Get the topic and payload
        topic = message.topic  # e.g., "google-assistant/cmnd/navimow_running"
        cmnd = message.payload.decode("utf-8")  # e.g., "Run"
        subtopic = topic.split("/")[-1]  # e.g., "navimow_running"
        subscribed_commands = self.mqtt_config.get("subscribe", {})

        # Check if the subtopic is in the subscribed commands
        if subtopic not in subscribed_commands:
            logger.warning("Received message on unsubscribed topic: %s", subtopic)
            return

        # Check if the command is in the subscribed commands
        if cmnd not in subscribed_commands[subtopic]:
            logger.warning("Received command not in subscribed commands: %s", cmnd)
            return

        # Get the command from the subscribed commands
        command = subscribed_commands[subtopic].get(cmnd)
        logger.info("Executing command: %s", command)

        try:
            self.assistant.call_assistant(command)
        except RuntimeError as e:
            logger.error("Error processing command: %s", e)

    def publish_to_mqtt(self, data: Dict[str, Any]) -> None:
        """Publish the data to the MQTT topic."""
        topic = self.server_config.get("MQTT_TOPIC")
        payload = {
            "sdk_calls_today": int(data["sdk_calls_today"]),
            "error": data["error"],
            "timestamp": (
                datetime.datetime.fromtimestamp(data["timestamp"]).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                if data["timestamp"]
                else None
            ),
        }
        for key, _value in self.mqtt_config.get("publish", {}).items():
            # check if the key is in the data
            payload[key] = data.get(key)
        payload_json = json.dumps(payload)
        logger.info("Publishing payload to topic: %s/stat", topic)
        try:
            self.client.publish(f"{topic}/stat", payload_json)
            logger.info("Published payload to topic: %s/stat", topic)
        except ValueError as e:
            logger.error("Failed to publish to topic %s/stat: %s", topic, e)
