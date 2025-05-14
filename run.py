"""Entry point for the Google Assistant MQTT Connect application."""

from src.main import MainApplication

if __name__ == "__main__":
    # Create an instance of the main application
    app = MainApplication()
    # Start the application's main loop
    app.run()
