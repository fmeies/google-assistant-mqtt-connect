"""
This module provides functionality to interact with an MQTT broker.
"""

import logging
import datetime
import json
import paho.mqtt.client as pahomqtt

from .assistant import call_assistant

logger = logging.getLogger(__name__)

MQTT_CLIENT = None


def on_message(_client, mqtt_config, message) -> None:
    """Callback function to handle incoming messages."""
    # get the topic and payload
    topic = message.topic  # e.g., "google-assistant/cmnd/navimow_running"
    cmnd = message.payload.decode("utf-8")  # e.g., "Run"
    subtopic = topic.split("/")[-1]  # e.g., "navimow_running"
    subscribed_commands = mqtt_config.get("subscribe", {})

    # check if the subtopic is in the subscribed commands
    if subtopic not in subscribed_commands:
        logger.warning("Received message on unsubscribed topic: %s", subtopic)
        return

    # check if the command is in the subscribed commands
    if cmnd not in subscribed_commands[subtopic]:
        logger.warning("Received command not in subscribed commands: %s", cmnd)
        return

    # get the command from the subscribed commands
    command = subscribed_commands[subtopic].get(cmnd)
    logger.info("Executing command: %s", command)

    try:
        call_assistant(command)
    except Exception as e:
        logger.error("Error processing command: %s", e)


def publish_to_mqtt(server_config, mqtt_config, data) -> None:
    """Publish the data to the MQTT topic."""
    topic = server_config.get("MQTT_TOPIC")
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
    for key, _value in mqtt_config.get("publish", {}).items():
        payload[key] = data[key]
    payload_json = json.dumps(payload)
    logger.info("Publishing payload to topic: %s/stat", topic)
    try:
        MQTT_CLIENT.publish(f"{topic}/stat", payload_json)
        logger.info("Published payload to topic: %s/stat", topic)
    except Exception as e:
        logger.error("Failed to publish to topic %s/stat: %s", topic, e)


def init_mqtt_client(server_config, mqtt_config) -> None:
    """Set up and return an MQTT client."""
    client_id = server_config["MQTT_CLIENT_ID"]
    server = server_config["MQTT_SERVER"]
    port = server_config["MQTT_PORT"]
    topic = server_config["MQTT_TOPIC"]
    user_name = server_config.get("MQTT_USERNAME")
    password = server_config.get("MQTT_PASSWORD")

    global MQTT_CLIENT
    MQTT_CLIENT = pahomqtt.Client(protocol=pahomqtt.MQTTv311)
    MQTT_CLIENT.user_data_set(client_id)
    if user_name and password:
        MQTT_CLIENT.username_pw_set(user_name, password)
    # add mqtt_config to userdata
    MQTT_CLIENT.user_data_set(mqtt_config)
    MQTT_CLIENT.on_message = on_message
    MQTT_CLIENT.reconnect_delay_set(min_delay=1, max_delay=120)
    MQTT_CLIENT.connect(server, port, 60)
    logger.info("Subscribing to topic: %s/cmnd/#", topic)
    MQTT_CLIENT.subscribe(f"{topic}/cmnd/#")
    MQTT_CLIENT.loop_start()
