"""
Main entry point for the application.
"""

import logging
import threading
import time

from .config import init_config
from .mqtt import init_mqtt_client, publish_to_mqtt
from .assistant import init_assistant
from .data import update_data

DEFAULT_GOOGLE_API_RELOAD_INTERVAL = 300

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        # logging.FileHandler("/var/log/connector.log"),  # Logs to a file
        logging.StreamHandler()  # Logs to stdout
    ],
)

logger = logging.getLogger(__name__)


def update_and_publish_data(server_config, mqtt_config) -> None:
    """Periodically update the status cache by querying the Google Assistant."""
    data = {}
    while True:
        request_pause = server_config.get("REQUEST_PAUSE_HOURS", [])
        current_hour = time.localtime().tm_hour
        if current_hour not in request_pause:
            data = update_data(mqtt_config)
        else:
            # log request pause hours
            # and skip data update
            logger.info(
                "Skipping data update during request pause hours: %s",
                str(request_pause),
            )
        publish_to_mqtt(server_config, mqtt_config, data)

        time.sleep(
            server_config.get(
                "GOOGLE_API_RELOAD_INTERVAL", DEFAULT_GOOGLE_API_RELOAD_INTERVAL
            )
        )


def main() -> None:
    """Main entry point for the application."""
    server_config, mqtt_config = init_config()
    init_mqtt_client(server_config, mqtt_config)
    init_assistant(server_config)

    # init thread, pass server_config to the function
    # to avoid circular import
    threading.Thread(
        target=update_and_publish_data, args=(server_config, mqtt_config), daemon=True
    ).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == "__main__":
    main()
