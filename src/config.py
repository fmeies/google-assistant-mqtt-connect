import logging
import json

# Configuration file paths
SERVER_CONFIG_PATH = ".env"
MQTT_CONFIG_PATH = "mqtt_config.json"

# Logger setup
logger = logging.getLogger(__name__)

server_config = {}
mqtt_config = {}

def init_config() -> tuple:
    """Initialize the configuration by loading from files."""
    global server_config, mqtt_config

    # Load server configuration
    load_config(server_config, SERVER_CONFIG_PATH)

    # Load MQTT configuration
    load_config(mqtt_config, MQTT_CONFIG_PATH)
    
    # Validate configurations
    if not all([
        server_config.get("MQTT_CLIENT_ID"),
        server_config.get("MQTT_SERVER"),
        server_config.get("MQTT_PORT"), 
        server_config.get("MQTT_TOPIC")]):
        raise ValueError("MQTT configuration is incomplete. Please check your .env file.")
    
    return server_config, mqtt_config

def load_config(config, path) -> None:
    """Load the configuration from a file."""
    try:
        with open(path, "r") as config_file:
            config.clear()
            config.update(json.load(config_file))
    except Exception as e:
        logger.error(f"Error loading config from {path}: {e}")