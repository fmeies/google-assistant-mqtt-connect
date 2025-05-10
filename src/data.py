import logging
import datetime
import time
import re

from .assistant import call_assistant
from .config import server_config, mqtt_config
from .mqtt import publish_to_mqtt

DEFAULT_GOOGLE_API_RELOAD_INTERVAL = 300

logger = logging.getLogger(__name__)

data_cache = {
    "timestamp": 0,
    "error": None,
    "sdk_calls_today": 0,
    "sdk_calls_today_date": None
}

def data_updater() -> None:
    """Periodically update the status cache by querying the Google Assistant."""
    while True:
        update_data()
        time.sleep(server_config.get("GOOGLE_API_RELOAD_INTERVAL", DEFAULT_GOOGLE_API_RELOAD_INTERVAL))

def update_data() -> None:
    """Update the status cache by querying the Google Assistant and publishing the results to MQTT."""
    try:
        global data_cache
        counter = 0
        for key, value in mqtt_config.get("publish", {}).items():
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
        
        data_cache["timestamp"] = time.time()
        data_cache["error"] = None
        
        today = datetime.date.today().isoformat()
        if data_cache.get("sdk_calls_today_date") != today:
            data_cache["sdk_calls_today"] = counter
            data_cache["sdk_calls_today_date"] = today
        else:
            data_cache["sdk_calls_today"] += counter
        
        publish_to_mqtt(data_cache)
    except Exception as e:
        logger.error(f"Error updating status cache: {e}")
        data_cache["error"] = str(e)
        data_cache["timestamp"] = time.time()
        for key in mqtt_config.get("publish", {}).keys():
            data_cache[key] = None

