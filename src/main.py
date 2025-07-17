"""
Main entry point for the application.
"""

import logging
import threading
import time
from typing import Any, Dict

from src.config import Config
from src.mqtt import MQTTClient
from src.assistant import GoogleAssistant
from src.data import DataUpdater

DEFAULT_GOOGLE_API_RELOAD_INTERVAL = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],  # Logs to stdout
)

logger = logging.getLogger(__name__)


# pylint: disable=R0903
class MainApplication:
    """Main application class for Google Assistant MQTT Connect."""

    config: Config
    server_config: Dict[str, Any]
    mqtt_config: Dict[str, Any]
    assistant: GoogleAssistant
    data_updater: DataUpdater
    mqtt_client: MQTTClient

    def __init__(self) -> None:
        """Initialize the application and its dependencies."""
        self.config = Config()
        self.server_config = self.config.get_server_config()
        self.mqtt_config = self.config.get_mqtt_config()
        self.assistant = GoogleAssistant(self.server_config)
        self.data_updater = DataUpdater(self.assistant, self.mqtt_config)
        self.mqtt_client = MQTTClient(
            self.assistant, self.server_config, self.mqtt_config
        )

    def _update_loop(self) -> None:
        """Periodically update the status cache by querying the Google Assistant."""
        while True:
            self.update_and_publish_data()
            time.sleep(
                self.server_config.get(
                    "GOOGLE_API_RELOAD_INTERVAL", DEFAULT_GOOGLE_API_RELOAD_INTERVAL
                )
            )

    def update_and_publish_data(self) -> None:
        """Update the data and publish it to MQTT."""
        request_pause = self.server_config.get("REQUEST_PAUSE_HOURS", [])
        current_hour = time.localtime().tm_hour
        # Check if we've actually fetched data before
        is_first_run = self.data_updater.data_cache.get("sdk_calls_today") == 0
        if current_hour not in request_pause or is_first_run:
            data = self.data_updater.update_data()
        else:
            logger.info(
                "Skipping data update during request pause hours: %s",
                str(request_pause),
            )
            data = self.data_updater.data_cache

        self.mqtt_client.publish_to_mqtt(data)

    def run(self) -> None:
        """Run the main application loop."""
        # Start the update and publish thread
        threading.Thread(target=self._update_loop, daemon=True).start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")


if __name__ == "__main__":
    app = MainApplication()
    app.run()
