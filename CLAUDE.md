# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the application
python run.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_main.py

# Run a single test
pytest tests/test_main.py::TestClassName::test_method_name

# Lint
pylint src/ tests/

# Type check
mypy src/

# Format
black src/ tests/
```

## Architecture

This is a Python bridge that connects Google Assistant (via text API) to an MQTT broker, enabling smart home automation for devices controllable through Google Assistant (originally built for a Segway Navimow robotic mower).

### Components

- **`src/config.py`** — Loads `.env` (server config) and `mqtt_config.json` (MQTT publish/subscribe mappings)
- **`src/assistant.py`** — Wraps `gassist_text` to send text commands to Google Assistant; authenticates via `token.json` (OAuth2); handles HTML response parsing via regex
- **`src/data.py`** — Iterates publish config entries, calls Google Assistant, applies regex extraction and result mapping, tracks daily API call count
- **`src/mqtt.py`** — Connects to MQTT broker; subscribes to `{MQTT_TOPIC}/cmnd/#`; publishes status to `{MQTT_TOPIC}/stat`
- **`src/main.py`** — Ties everything together; runs a background thread that calls `DataUpdater.update_data()` every `GOOGLE_API_RELOAD_INTERVAL` seconds, then publishes via MQTT

### Data Flow

**Status updates (background thread):**
1. Every N seconds, if not in `REQUEST_PAUSE_HOURS`, call Google Assistant with each "publish" command from `mqtt_config.json`
2. Extract values via regex, map through `result_map` if configured
3. Publish JSON payload to `{MQTT_TOPIC}/stat` including `sdk_calls_today`, `error`, `timestamp`, and all extracted data keys

**Command reception (MQTT callback):**
1. Message arrives on `{MQTT_TOPIC}/cmnd/{subtopic}`
2. Validate subtopic and payload against "subscribe" config
3. Send mapped command to Google Assistant

### Configuration

- **`.env`** — MQTT connection settings, `GOOGLE_API_RELOAD_INTERVAL`, `GOOGLE_API_LANGUAGE`, `REQUEST_PAUSE_HOURS` (hours to skip API calls, e.g., overnight)
- **`mqtt_config.json`** — Two sections:
  - `publish`: list of `{command, extract_regex, result_map, key}` entries — what to query and how to parse responses
  - `subscribe`: `{subtopic: {command_value: "google assistant phrase"}}` — incoming MQTT commands mapped to Assistant phrases
- **`token.json`** — Google OAuth2 token (generated via `google-auth-oauthlib`; not committed)

### Rate Limiting

The Google Assistant text API has a daily call limit. `REQUEST_PAUSE_HOURS` is used to suppress API calls during low-value hours (e.g., overnight). During pause hours, the last cached data is re-published instead of making new API calls.
