import logging

from google.oauth2.credentials import Credentials  # Third-party library
from gassist_text import TextAssistant  # Local import

OAUTH2_TOKEN_PATH = "token.json"

logger = logging.getLogger(__name__)

text_assistant = None

def init_assistant() -> None:
    """Initialize the Google Assistant."""
    global text_assistant
    creds = Credentials.from_authorized_user_file(OAUTH2_TOKEN_PATH)
    text_assistant = TextAssistant(creds, "en-US", display=True)

def call_assistant(command):
    """Send a command to the Google Assistant and process the response."""
    try:
        response = text_assistant.assist(command)
        if isinstance(response, tuple):
            response = response[1]
        if isinstance(response, bytes):
            response = response.decode("utf-8")
        if isinstance(response, str):
            start = response.find('<div class="show_text_content">')
            end = response.find('</div>', start)
            if start != -1 and end != -1:
                response = response[start + len('<div class="show_text_content">'):end]
            else:
                response = "No valid response found."
        return response
    except Exception as e:
        raise RuntimeError(f"Assistant error: {e}")


