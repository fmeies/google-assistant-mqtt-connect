"""
Google Assistant Integration Module
This module provides functionality to interact with the Google Assistant API.
"""

import logging
import re
from typing import Any, Dict
from google.oauth2.credentials import Credentials # pylint: disable=import-error
from gassist_text import TextAssistant  # pylint: disable=import-error

OAUTH2_TOKEN_PATH = "token.json"
DEFAULT_LANGUAGE = "en-US"

logger = logging.getLogger(__name__)


# pylint: disable=R0903
class GoogleAssistant:
    """Encapsulates the Google Assistant API logic."""

    text_assistant: TextAssistant

    def __init__(self, server_config: Dict[str, Any]) -> None:
        """Initialize the Google Assistant."""
        creds = Credentials.from_authorized_user_file(OAUTH2_TOKEN_PATH)
        lang = server_config.get("GOOGLE_API_LANGUAGE", DEFAULT_LANGUAGE)
        self.text_assistant = TextAssistant(creds, lang, display=True)

    def _extract_response(self, response: str) -> str:
        """Extract the relevant part of the response from the Google Assistant."""
        match = re.search(r'<div class="show_text_content">(.*?)</div>', response)
        return match.group(1) if match else "No valid response found."

    def call_assistant(self, command: str) -> str:
        """Send a command to the Google Assistant and process the response."""
        logger.info("Sending command to Google Assistant: %s", command)

        try:
            response = self.text_assistant.assist(command)
            if isinstance(response, tuple):
                response = response[1]
            if isinstance(response, bytes):
                response = response.decode("utf-8")
            if isinstance(response, str):
                response = self._extract_response(response)
            return response
        except Exception as e:
            logger.error("Error while sending command to Google Assistant: %s", e)
            raise RuntimeError("Assistant error") from e
