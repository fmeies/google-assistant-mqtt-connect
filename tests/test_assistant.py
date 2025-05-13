"""Unit tests for the GoogleAssistant class and assistant interaction."""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from src.assistant import GoogleAssistant


class TestGoogleAssistant(unittest.TestCase):
    """Test cases for the GoogleAssistant class."""

    @patch("src.assistant.TextAssistant")
    @patch("src.assistant.Credentials.from_authorized_user_file")
    def test_call_assistant(
        self, _mock_creds: MagicMock, mock_text_assistant: MagicMock
    ) -> None:
        """Test the call_assistant method."""
        # Mock server configuration
        server_config: Dict[str, Any] = {"GOOGLE_API_LANGUAGE": "en-US"}

        # Mock TextAssistant behavior
        mock_text_assistant_instance = mock_text_assistant.return_value
        mock_text_assistant_instance.assist.return_value = (
            "",
            b'<div class="show_text_content">Test Response</div>',
        )

        # Initialize GoogleAssistant
        assistant = GoogleAssistant(server_config)

        # Call the assistant
        response: str = assistant.call_assistant("Test Command")

        # Assert the response
        self.assertEqual(response, "Test Response")
        mock_text_assistant_instance.assist.assert_called_once_with("Test Command")


if __name__ == "__main__":
    unittest.main()
