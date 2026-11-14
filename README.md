# Google Assistant MQTT Connector

This project is a connector for the Google Assistant SDK. It is based on by the [Google Assistant SDK Home Assistant Integration](https://www.home-assistant.io/integrations/google_assistant_sdk) and [this discussion about a Segway Navimow home assistant integration](https://community.home-assistant.io/t/segway-navimow/435023/1). Thank you to the authors of these projects for their work and inspiration.

This connector allows you to control your devices using mqtt to make it easier to integrate certain devices with smart home systems, e.g., [openHAB](https://www.openhab.org). This is especially useful for devices that do not have a native integration with the smart home system you are using but can be controlled via Google Assistant.

As a proof of concept, I added a simple configuration to control a Segway Navimow i105 mower. If your device has a Google Home integration, there's a good chance that this connector will work for you as well.

## Configuration files

> **Upgrading from an older version?** The config files moved from the project root to `config/`, and `.env` is now `server_config.json` (same content):
> `mkdir -p config && mv .env config/server_config.json && mv token.json config/` — then copy your `mqtt_config.json` to `config/` (the repo version moved to `config.example/`).

The connector reads three files from the `config/` directory. They contain secrets or local settings, so the whole directory is **never committed** (see `.gitignore`). Start from the templates:

```
cp -r config.example config
```

```
config/
├── server_config.json   # MQTT connection, API interval, language, pause hours
├── mqtt_config.json     # what to query and which MQTT commands to accept (Navimow example)
└── token.json           # Google OAuth2 token, created in the next steps
```

The same directory is used locally and by Docker. A different location can be set with the `CONFIG_DIR` environment variable.

### Create Google Assistant API client ID and client secret

Follow the instructions in the [Google Assistant SDK Home Assistant Integration](https://www.home-assistant.io/integrations/google_assistant_sdk#scenario-2-you-do-not-have-credentials-set-up-yet) to create a Google Assistant API client ID and client secret. Download the `client_secret.json` file.

### Create a token.json file from the secrets file

The following step opens a browser window to authenticate your Google account. Log in with the same account you used to create the client ID and client secret, and allow the application to access your Google Assistant. Then paste the console output into `config/token.json`.

```
pip3 install google-auth-oauthlib
python3 -m google_auth_oauthlib.tool --client-secrets client_secret.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype
```

### Adjust the server configuration

Adjust `config/server_config.json` to your needs. Please note that there is a limitation of 500 calls to the Google Assistant API per day. If you exceed this limit, you will need to wait until the next day to use the connector again. `REQUEST_PAUSE_HOURS` are local hours, so set the container's time zone (see below).

### Adjust the mqtt configuration

Have a look at `config/mqtt_config.json` and adjust it to your needs. Status messages are sent to the `stat` subtopic of the configured main topic (default is `google_assistant`). The connector subscribes to the `cmnd` subtopic of the main topic.

## Run with Docker Compose (recommended)

With the `config/` directory next to `docker-compose.yml`:

```bash
docker compose pull && docker compose up -d   # prebuilt image from GHCR
docker compose logs -f

# Testing local changes: build under the same tag, then start without pulling
docker build -t ghcr.io/fmeies/google-assistant-mqtt-connect:latest .
docker compose up -d --pull never
```

The config directory is mounted read-only; no credentials are baked into the image. The time zone defaults to `Europe/Berlin` and can be overridden with `TZ=... docker compose up -d`.

## Run with Docker

```bash
docker run -d --name google-assistant-mqtt-connect --restart unless-stopped \
  -v "$(pwd)/config:/config:ro" -e TZ=Europe/Berlin \
  ghcr.io/fmeies/google-assistant-mqtt-connect:latest
```

Every push to `main` publishes `ghcr.io/fmeies/google-assistant-mqtt-connect:latest` (linux/amd64, linux/arm64 and linux/arm/v7, i.e. also Raspberry Pis with a 32-bit OS) after the tests pass, plus a `sha-<commit>` tag. Git tags `vX.Y.Z` publish matching version tags to pin in production.

## Run locally with Python

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements-dev.txt
python3 run.py
```

The connector reads `config/` relative to the working directory. Stop the connector with `Ctrl+C`.

## Run the tests and code quality tools

```
pytest -v
pylint src tests run.py
mypy src
black src tests run.py
```

## How to use the connector

Example 1: status message sent to `google_assistant/stat/#`

```json
{
	"sdk_calls_today": 12,
	"error": "",
	"timestamp": "2025-07-20 16:56:41",
	"navimow_running_status": "Dock",
	"navimow_battery_status": "100"
}
```

Example 2: to start the mower, publish a message to the `google_assistant/cmnd/navimow_running` topic with the payload `Run`.

Example 3: to send the mower to the dock, publish a message to the `google_assistant/cmnd/navimow_running` topic with the payload `Dock`.