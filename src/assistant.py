"""
Google Assistant Integration Module
This module provides functionality to interact with the Google Assistant API.
"""

import logging
import re

from google.oauth2.credentials import Credentials  # Third-party library
from gassist_text import TextAssistant  # Local import

OAUTH2_TOKEN_PATH = "token.json"
DEFAULT_LANGUAGE = "en-US"

logger = logging.getLogger(__name__)

TEXT_ASSISTANT = None


def init_assistant(server_config) -> None:
    """Initialize the Google Assistant."""
    global TEXT_ASSISTANT
    creds = Credentials.from_authorized_user_file(OAUTH2_TOKEN_PATH)
    lang = server_config.get("GOOGLE_API_LANGUAGE", DEFAULT_LANGUAGE)
    TEXT_ASSISTANT = TextAssistant(creds, lang, display=True)


def extract_response(response):
    """Extract the relevant part of the response from the Google Assistant."""
    match = re.search(r'<div class="show_text_content">(.*?)</div>', response)
    return match.group(1) if match else "No valid response found."


def call_assistant(command):
    """Send a command to the Google Assistant and process the response."""
    logger.info("Sending command to Google Assistant: %s", command)

    try:
        response = TEXT_ASSISTANT.assist(command)
        if isinstance(response, tuple):
            response = response[1]
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        if isinstance(response, str):
            response = extract_response(response)
        return response
    except Exception as e:
        logger.error("Error while sending command to Google Assistant: %s", e)
        raise RuntimeError("Assistant error") from e
