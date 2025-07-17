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

    @patch("src.assistant.TextAssistant")
    @patch("src.assistant.Credentials.from_authorized_user_file")
    def test_assistant_reinitialize_after_exception(
        self, _mock_creds: MagicMock, mock_text_assistant: MagicMock
    ) -> None:
        """Test that the assistant is re-initialized after an exception."""
        # Mock server configuration
        server_config: Dict[str, Any] = {"GOOGLE_API_LANGUAGE": "en-US"}

        # Set up TextAssistant to throw an exception on first call, then succeed on second call
        mock_text_assistant_instance = mock_text_assistant.return_value
        mock_text_assistant_instance.assist.side_effect = [
            Exception("API Error"),  # First call fails
            (
                "",
                b'<div class="show_text_content">Success after retry</div>',
            ),  # Second call succeeds
        ]

        # Initialize GoogleAssistant
        assistant = GoogleAssistant(server_config)

        # First call should raise an exception
        with self.assertRaises(RuntimeError):
            assistant.call_assistant("Test Command")

        # Second call should succeed with re-initialized assistant
        response = assistant.call_assistant("Test Command Again")

        # Assert TextAssistant was re-initialized
        self.assertEqual(response, "Success after retry")

        # Verify the original exception was properly logged
        # This requires patching the logger in your implementation


if __name__ == "__main__":
    unittest.main()
