"""
This module handles the data update process for the Google Assistant integration.
"""

import logging
import datetime
import time
import re
from typing import Any, Dict

from src.assistant import GoogleAssistant

logger = logging.getLogger(__name__)


# pylint: disable=R0903
class DataUpdater:
    """Handles the data update process for the Google Assistant integration."""

    assistant: GoogleAssistant
    mqtt_config: Dict[str, Any]
    data_cache: Dict[str, Any]

    def __init__(self, assistant: GoogleAssistant, mqtt_config: Dict[str, Any]) -> None:
        self.assistant = assistant
        self.mqtt_config = mqtt_config
        self.data_cache = {
            "timestamp": 0,
            "error": None,
            "sdk_calls_today": 0,
            "sdk_calls_today_date": None,
        }

    def update_data(self) -> Dict[str, Any]:
        """Update the status cache by querying the Google Assistant
        and publishing the results to MQTT."""
        logger.info("Starting data update...")
        try:
            counter = 0
            for key, value in self.mqtt_config.get("publish", {}).items():
                logger.debug("Processing key: %s, value: %s", key, value)
                command = value["command"]
                regex_str = value.get("regex", "(.*)")
                result_map = value.get("result_map", {})
                answer = self.assistant.call_assistant(command)
                regex = re.compile(regex_str)
                match = re.search(regex, answer)
                counter += 1
                if match:
                    result = match.group(1)
                else:
                    result = "No valid response found."
                if result in result_map:
                    self.data_cache[key] = result_map[result]
                else:
                    self.data_cache[key] = result
                logger.info("Received data for key %s: %s", key, self.data_cache[key])

            self.data_cache["timestamp"] = time.time()
            self.data_cache["error"] = ""

            today = datetime.date.today().isoformat()
            if self.data_cache.get("sdk_calls_today_date") != today:
                self.data_cache["sdk_calls_today"] = counter
                self.data_cache["sdk_calls_today_date"] = today
            else:
                self.data_cache["sdk_calls_today"] += counter

            logger.info("Data update completed successfully.")
        except Exception as e:
            logger.error("Error updating status cache: %s", e)
            self.data_cache["error"] = re.sub(r"[\n\t]", "", str(e))
            self.data_cache["timestamp"] = time.time()
            for key in self.mqtt_config.get("publish", {}).keys():
                self.data_cache[key] = None

        return self.data_cache
