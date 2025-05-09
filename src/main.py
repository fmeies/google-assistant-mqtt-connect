import threading
import time
import logging

from config import (
    init_config,
    server_config
)
from mqtt import (
    init_mqtt_client
)
from assistant import (
    init_assistant,
)
from data import (
    data_updater
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        #logging.FileHandler("/var/log/connector.log"),  # Logs to a file
        logging.StreamHandler()         # Logs to stdout
    ]
)

logger = logging.getLogger(__name__)

def main() -> None:
    """Main entry point for the application."""
    init_config()
    init_mqtt_client(server_config)
    init_assistant()
    
    threading.Thread(target=data_updater, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()