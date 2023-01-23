# DAS Python Wireless Sensor Modules

Wireless sensor firmware based on Python.

## Getting Started

For an overview of the wireless module usage from a user's view, see the [Notion manual](https://www.notion.so/Wireless-module-usage-manual-cd7e948418d040d991a50c91815e63e9).

### Set up development environment

Make sure to use Visual Studio Code for the best development experience.

You will need to create a local version of `config.py` (`cp src/config.example.py src/config.py`) and change some settings.

| Name        | Description                        |
| ----------- | ---------------------------------- |
| MQTT_BROKER | IP address of the MQTT broker      |
| USERNAME    | Username to connect to MQTT broker |
| PASSWORD    | Password to connect to MQTT broker |
| PORT        | Port to connect the anemometer to  |
