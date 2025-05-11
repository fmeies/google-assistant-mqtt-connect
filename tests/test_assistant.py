import unittest
from unittest.mock import patch, MagicMock
from src.assistant import init_assistant, call_assistant

class TestAssistant(unittest.TestCase):
    @patch("src.assistant.Credentials.from_authorized_user_file")
    @patch("src.assistant.TextAssistant")
    def test_init_assistant(self, mock_text_assistant, mock_credentials):
        """Test the initialization of the Google Assistant."""
        mock_credentials.return_value = MagicMock()
        mock_text_assistant.return_value = MagicMock()
        
        server_config = {
            "GOOGLE_API_LANGUAGE": "de-DE"
        }
        init_assistant(server_config)
        
        mock_credentials.assert_called_once_with("token.json")
        # assert the TextAssistant is initialized with the correct parameters
        mock_text_assistant.assert_called_once_with(
            mock_credentials.return_value,
            server_config["GOOGLE_API_LANGUAGE"],
            display=True
        )

    @patch("src.assistant.text_assistant")
    def test_call_assistant(self, mock_text_assistant):
        """Test sending a command to the Google Assistant."""
        mock_text_assistant.assist.return_value = ("", b"<div class=\"show_text_content\">Test Response</div>")
        
        response = call_assistant("Test Command")
        
        self.assertEqual(response, "Test Response")

if __name__ == "__main__":
    unittest.main()