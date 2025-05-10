
import logging
import datetime
import json
import paho.mqtt.client as pahomqtt

from .assistant import call_assistant

logger = logging.getLogger(__name__)

mqtt_client = None

def on_message(client, mqtt_config, message) -> None:
    """Callback function to handle incoming messages."""
    # get the topic and payload
    topic = message.topic # e.g., "google-assistant/cmnd/navimow_running"
    cmnd = message.payload.decode("utf-8") # e.g., "Run"
    subtopic = topic.split("/")[-1] # e.g., "navimow_running"
    subscribed_commands = mqtt_config.get("subscribe", {})
    
    # check if the subtopic is in the subscribed commands
    if subtopic not in subscribed_commands:
        logger.warning(f"Received message on unsubscribed topic: {subtopic}")
        return
    
    # check if the command is in the subscribed commands
    if cmnd not in subscribed_commands[subtopic]:
        logger.warning(f"Received command not in subscribed commands: {cmnd}")
        return
    
    # get the command from the subscribed commands
    command = subscribed_commands[subtopic].get(cmnd)
    logger.info(f"Executing command: {command}")
    
    try:
        call_assistant(command)
    except Exception as e:
        logger.error(f"Error processing command: {e}")

def publish_to_mqtt(server_config, mqtt_config, data) -> None:
    """Publish the data to the MQTT topic."""
    topic = server_config.get("MQTT_TOPIC")
    payload = {
        "sdk_calls_today": int(data["sdk_calls_today"]),
        "error": data["error"],
        "timestamp": datetime.datetime.fromtimestamp(data["timestamp"]).strftime('%Y-%m-%d %H:%M:%S') if data["timestamp"] else None
    }
    for key, value in mqtt_config.get("publish", {}).items():
        payload[key] = data[key]
    payload_json = json.dumps(payload)
    logger.info(f"Publishing payload to topic: {topic}/stat")
    mqtt_client.publish(f"{topic}/stat", payload_json)

def init_mqtt_client(server_config, mqtt_config) -> None:
    """Set up and return an MQTT client."""
    client_id = server_config["MQTT_CLIENT_ID"]
    server = server_config["MQTT_SERVER"]
    port = server_config["MQTT_PORT"]
    topic = server_config["MQTT_TOPIC"]
    user_name = server_config.get("MQTT_USERNAME")
    password = server_config.get("MQTT_PASSWORD")

    global mqtt_client
    mqtt_client = pahomqtt.Client(protocol=pahomqtt.MQTTv311)
    mqtt_client.user_data_set(client_id)
    if user_name and password:
        mqtt_client.username_pw_set(user_name, password)
    # add mqtt_config to userdata
    mqtt_client.user_data_set(mqtt_config)
    mqtt_client.on_message = on_message
    mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
    mqtt_client.connect(server, port, 60)
    logger.info(f"Subscribing to topic: {topic}/cmnd/#")
    mqtt_client.subscribe(f"{topic}/cmnd/#")
    mqtt_client.loop_start()
