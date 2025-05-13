import unittest
from unittest.mock import patch
from src.config import Config


class TestConfig(unittest.TestCase):
    @patch(
        "json.load",
        return_value={
            "MQTT_CLIENT_ID": "test_id",
            "MQTT_SERVER": "localhost",
            "MQTT_PORT": 1883,
            "MQTT_TOPIC": "test/topic",
        },
    )
    @patch("builtins.open")  # Mock open, but we don't need to specify read_data
    def test_init_config(self, mock_open_file, mock_json_load):
        """Test the init_config method."""
        config = Config()

        server_config = config.get_server_config()

        self.assertEqual(server_config["MQTT_CLIENT_ID"], "test_id")
        self.assertEqual(server_config["MQTT_SERVER"], "localhost")
        self.assertEqual(server_config["MQTT_PORT"], 1883)
        self.assertEqual(server_config["MQTT_TOPIC"], "test/topic")
        mock_open_file.assert_called()
        mock_json_load.assert_called()

    @patch("json.load", return_value={})  # Mock json.load to return an empty object
    @patch("builtins.open")  # Mock open
    def test_validate_config_missing_keys(self, _mock_open_file, _mock_json_load):
        """Test validate_config raises an error for missing keys."""
        with self.assertRaises(ValueError) as context:
            Config()
        self.assertIn(
            "Missing required server configuration keys", str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
