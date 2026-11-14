"""
Google Assistant Integration Module
This module provides functionality to interact with the Google Assistant API.
"""

import logging
import re
from typing import Any, Dict, Optional
from google.oauth2.credentials import Credentials  # pylint: disable=import-error
from gassist_text import TextAssistant  # type: ignore  # pylint: disable=import-error

from src.config import OAUTH2_TOKEN_FILE, config_file_path

DEFAULT_LANGUAGE = "en-US"

logger = logging.getLogger(__name__)


# pylint: disable=R0903
class GoogleAssistant:
    """Encapsulates the Google Assistant API logic."""

    creds: Credentials
    lang: str
    text_assistant: TextAssistant

    def __init__(self, server_config: Dict[str, Any]) -> None:
        """Initialize the Google Assistant."""
        self.creds = Credentials.from_authorized_user_file(
            config_file_path(OAUTH2_TOKEN_FILE)
        )
        self.lang = server_config.get("GOOGLE_API_LANGUAGE", DEFAULT_LANGUAGE)
        self._init_text_assistant()

    def _init_text_assistant(self) -> None:
        """Initialize the Text Assistant with the current credentials and language."""
        self.text_assistant = TextAssistant(self.creds, self.lang, display=True)

    def _extract_response(self, response: str) -> str:
        """Extract the relevant part of the response from the Google Assistant."""
        match = re.search(r'<div class="show_text_content">(.*?)</div>', response)
        return match.group(1) if match else "No valid response found."

    def call_assistant(self, command: str) -> Optional[str]:
        """Send a command to the Google Assistant and return the extracted answer.

        Returns None if the Assistant sent no HTML response.
        """
        logger.info("Sending command to Google Assistant: %s", command)

        try:
            _text, html, _audio = self.text_assistant.assist(command)
        except Exception as e:
            logger.error("Error while sending command to Google Assistant: %s", e)
            self._init_text_assistant()
            raise RuntimeError("Assistant error. Re-init Text Assistant") from e

        if html is None:
            return None
        return self._extract_response(html.decode("utf-8"))
