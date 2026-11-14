"""Unit tests for the Config class and configuration loading/validation."""

import unittest
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from src.config import Config, config_file_path

VALID_SERVER_CONFIG: Dict[str, Any] = {
    "MQTT_CLIENT_ID": "test_id",
    "MQTT_SERVER": "localhost",
    "MQTT_PORT": 1883,
    "MQTT_TOPIC": "test/topic",
}


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""

    @patch("json.load", return_value=VALID_SERVER_CONFIG)
    @patch("builtins.open")  # Mock open, but we don't need to specify read_data
    def test_init_config(
        self, mock_open_file: MagicMock, mock_json_load: MagicMock
    ) -> None:
        """Test the init_config method."""
        config: Config = Config()
        server_config: Dict[str, Any] = config.get_server_config()

        self.assertEqual(server_config["MQTT_CLIENT_ID"], "test_id")
        self.assertEqual(server_config["MQTT_SERVER"], "localhost")
        self.assertEqual(server_config["MQTT_PORT"], 1883)
        self.assertEqual(server_config["MQTT_TOPIC"], "test/topic")
        mock_open_file.assert_called()
        mock_json_load.assert_called()

    @patch("json.load", return_value={})  # Mock json.load to return an empty object
    @patch("builtins.open")  # Mock open
    def test_validate_config_missing_keys(
        self, _mock_open_file: MagicMock, _mock_json_load: MagicMock
    ) -> None:
        """Test validate_config raises an error for missing keys."""
        with self.assertRaises(ValueError) as context:
            Config()
        self.assertIn(
            "Missing required server configuration keys", str(context.exception)
        )

    @patch.dict("os.environ", {}, clear=True)
    def test_config_file_path_defaults_to_config_subdirectory(self) -> None:
        """Without CONFIG_DIR, config files are read from ./config."""
        self.assertEqual(config_file_path("token.json"), "config/token.json")

    @patch.dict("os.environ", {"CONFIG_DIR": "/config"})
    def test_config_file_path_uses_config_dir(self) -> None:
        """CONFIG_DIR redirects all config files, e.g. to a container volume."""
        self.assertEqual(config_file_path("token.json"), "/config/token.json")

    @patch.dict("os.environ", {"CONFIG_DIR": "/config"})
    @patch("json.load", return_value=VALID_SERVER_CONFIG)
    @patch("builtins.open")
    def test_config_reads_files_from_config_dir(
        self, mock_open_file: MagicMock, _mock_json_load: MagicMock
    ) -> None:
        """Server and MQTT config are both loaded from CONFIG_DIR."""
        Config()
        opened_paths = [call.args[0] for call in mock_open_file.call_args_list]
        self.assertEqual(
            opened_paths, ["/config/server_config.json", "/config/mqtt_config.json"]
        )


if __name__ == "__main__":
    unittest.main()
