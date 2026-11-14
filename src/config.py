"""
Provides configuration logic for the application.
"""

import json
import logging
import os
from typing import Any, Dict, Optional

# Lets a container mount all config files (including the OAuth token) as one directory
CONFIG_DIR_ENV_VAR = "CONFIG_DIR"
DEFAULT_CONFIG_DIR = "config"
SERVER_CONFIG_FILE = "server_config.json"
MQTT_CONFIG_FILE = "mqtt_config.json"
OAUTH2_TOKEN_FILE = "token.json"

# Logger setup
logger = logging.getLogger(__name__)


def config_file_path(filename: str) -> str:
    """Return the path of a config file inside the configured config directory."""
    config_dir = os.environ.get(CONFIG_DIR_ENV_VAR, DEFAULT_CONFIG_DIR)
    return os.path.join(config_dir, filename)


class Config:
    """Handles loading and validation of server and MQTT configurations."""

    server_config_path: str
    mqtt_config_path: str
    server_config: Dict[str, Any]
    mqtt_config: Dict[str, Any]

    def __init__(
        self,
        server_config_path: Optional[str] = None,
        mqtt_config_path: Optional[str] = None,
    ) -> None:
        self.server_config_path = server_config_path or config_file_path(
            SERVER_CONFIG_FILE
        )
        self.mqtt_config_path = mqtt_config_path or config_file_path(MQTT_CONFIG_FILE)
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
