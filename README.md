# Google Assistant MQTT Connector

This project is a connector for the Google Assistant SDK. It is based on by the [Google Assistant SDK Home Assistant Integration](https://www.home-assistant.io/integrations/google_assistant_sdk) and [this discussion about a Segway Navimow home assistant integration](https://community.home-assistant.io/t/segway-navimow/435023/1). Thank you to the authors of these projects for their work and inspiration.

This connector allows you to control your devices using mqtt to make it easier to integrate certain devices with smart home systems, e.g., [openHAB](https://www.openhab.org). This is especially useful for devices that do not have a native integration with the smart home system you are using but can be controlled via Google Assistant.

As a proof of concept, I added a simple configuration to control a Segway Navimow i105 mower. If your device has a Google Home integration, there's a good chance that this connector will work for you as well.

## Create a virtual environment and install the required packages

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

## Create Google Assistant API client ID and client secret

Follow the instructions in the [Google Assistant SDK Home Assistant Integration](https://www.home-assistant.io/integrations/google_assistant_sdk#scenario-2-you-do-not-have-credentials-set-up-yet) to create a Google Assistant API client ID and client secret. Download the `client_secret.json` file and place it in the root directory of the project.

## Create a token.json file from the secrets file

The following step will open a browser window to authenticate your Google account. You will need to log in with the same account you used to create the client ID and client secret. After you have logged in, you will be asked to allow the application to access your Google Assistant. After you have allowed the application, paste the console output into a file named `token.json` located in the root directory of the project. This file will be used to authenticate the connector with the Google Assistant API.

```
python3 -m google_auth_oauthlib.tool --client-secrets client_secret.json --scope https://www.googleapis.com/auth/assistant-sdk-prototype
```

## Adjust the server configuration

Copy the `env_example` file to `.env` and adjust the values to your needs. Please note that there is a limitation of 500 calls to the Google Assistant API per day. If you exceed this limit, you will need to wait until the next day to use the connector again.

## Adjust the mqtt configuration

Have a look at the `mqtt_config.json` file. You can adjust the configuration to your needs. Status messages are sent to the `stat` subtopic of the configured main topic. The connector subscribes to the `cmnd` subtopic of the main topic.

## Run the connector

Start the connector with the following command. The connector will run in the foreground and print log messages to the console. You can stop the connector with `Ctrl+C`.

```
python3 run.py
```

Alternatively, you can create a systemd service to run the connector in the background. 

## Run the tests

You can run the tests with the following command.

```
pytest -v
```

## Run the linter and other code quality tools

You can run additional code quality tools with the following commands.

```
pylint src tests run.py
mypy src tests
black src tests run.py
```

Do you have a token.json in the root directory of the project? If not, please follow the instructions in README to create one.