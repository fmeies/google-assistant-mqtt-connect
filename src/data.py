"""
This module handles the data update process for the Google Assistant integration.
"""

import logging
import datetime
import time
import re

from .assistant import call_assistant

logger = logging.getLogger(__name__)

data_cache = {
    "timestamp": 0,
    "error": None,
    "sdk_calls_today": 0,
    "sdk_calls_today_date": None,
}


def update_data(mqtt_config) -> dict:
    """Update the status cache by querying the Google Assistant
    and publishing the results to MQTT."""
    logger.info("Starting data update...")
    try:
        counter = 0
        for key, value in mqtt_config.get("publish", {}).items():
            logger.debug("Processing key: %s, value: %s", key, value)
            command = value["command"]
            regex_str = value.get("regex", "(.*)")
            result_map = value.get("result_map", {})
            answer = call_assistant(command)
            regex = re.compile(regex_str)
            match = re.search(regex, answer)
            counter += 1
            if match:
                result = match.group(1)
            else:
                result = "No valid response found."
            if result in result_map:
                data_cache[key] = result_map[result]
            else:
                data_cache[key] = result
            logger.info("Received data for key %s: %s", key, data_cache[key])

        data_cache["timestamp"] = time.time()
        data_cache["error"] = ""

        today = datetime.date.today().isoformat()
        if data_cache.get("sdk_calls_today_date") != today:
            data_cache["sdk_calls_today"] = counter
            data_cache["sdk_calls_today_date"] = today
        else:
            data_cache["sdk_calls_today"] += counter

        logger.info("Data update completed successfully.")
    except Exception as e:
        logger.error("Error updating status cache: %s", e)
        data_cache["error"] = re.sub(r"[\n\t]", "", str(e))
        data_cache["timestamp"] = time.time()
        for key in mqtt_config.get("publish", {}).keys():
            data_cache[key] = None

    return data_cache
