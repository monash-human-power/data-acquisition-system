# Crash Alert

*This directory contains scripts to listen to the crash detection system and send alerts to subscribed users' devices*


- [Crash Alert](#crash-alert)
  - [Basic Setup and Usage](#basic-setup-and-usage)
  - 


## Basic Setup and Usage
These steps assume that you have [poetry](https://python-poetry.org/) installed.

```bash
# Move into crash_alert directory
cd crash_alert

# Install dependencies
poetry install

# Enter a poetry environment 
poetry shell
```


<br/>

## [V3 MQTT Recorder](/DAS/das/V3_mqtt_recorder.py)
The command line tool allows for mqtt messages on any topic to be logged and recorded to a mysql file.

To start this script automatically, see [the services README.md](/services/README.md).

### Usage
```
# General command
poetry run python -m das.V3_mqtt_recorder [TOPICS] [FLAGS]

# Subscribe to all topics on the V3 bike
poetry run python -m das.V3_mqtt_recorder /v3/#  -v

# Subscribe just BOOST and wireless module topics
poetry run python -m das.V3_mqtt_recorder /v3/wireless_module/# boost/# -v
```
