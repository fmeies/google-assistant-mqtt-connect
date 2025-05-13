"""
Provides configuration logic for the application.
"""

import json
import logging
from typing import Any, Dict

# Configuration file paths
SERVER_CONFIG_PATH = ".env"
MQTT_CONFIG_PATH = "mqtt_config.json"

# Logger setup
logger = logging.getLogger(__name__)


class Config:
    """Handles loading and validation of server and MQTT configurations."""

    server_config_path: str
    mqtt_config_path: str
    server_config: Dict[str, Any]
    mqtt_config: Dict[str, Any]

    def __init__(
        self, server_config_path=SERVER_CONFIG_PATH, mqtt_config_path=MQTT_CONFIG_PATH
    ) -> None:
        self.server_config_path = server_config_path
        self.mqtt_config_path = mqtt_config_path
        self.server_config = {}
        self.mqtt_config = {}
        self._load_configs()
        self._validate_configs()

    def _load_configs(self):
        """Load server and MQTT configurations from files."""
        try:
            with open(self.server_config_path, "r", encoding="utf-8") as server_file:
                self.server_config = json.load(server_file)
            with open(self.mqtt_config_path, "r", encoding="utf-8") as mqtt_file:
                self.mqtt_config = json.load(mqtt_file)
        except Exception as e:
            logger.error("Error loading configuration files: %s", e)
            raise ValueError("Failed to load configuration files") from e

    def _validate_configs(self):
        """Validate the loaded configurations."""
        required_keys = ["MQTT_CLIENT_ID", "MQTT_SERVER", "MQTT_PORT", "MQTT_TOPIC"]
        missing_keys = [key for key in required_keys if key not in self.server_config]
        if missing_keys:
            raise ValueError(
                f"Missing required server configuration keys: {missing_keys}"
            )

    def get_server_config(self) -> Dict[str, Any]:
        """Return the server configuration."""
        return self.server_config

    def get_mqtt_config(self) -> Dict[str, Any]:
        """Return the MQTT configuration."""
        return self.mqtt_config
