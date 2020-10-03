# DAS

*This directory contains scripts to log and test various components of the data data-acquisition-system*



## Basic Setup and Usage
These steps assume that you are in the data-acquisition-system root directory.
1. `cd DAS`
2. `poetry install`
3. `poetry shell`
4. Run any DAS command, _e.g._ `python -m das.mqtt_recorder`



## [MQTT Recorder](/DAS/das/mqtt_recorder.py)
The command line tool allows for mqtt messages on any topic to be logged and recorded to a csv file. The saved csv files will be stored in the `das/csv_data`. 

### Usage
```
# General command
python -m das.mqtt_recorder [TOPICS] [FLAGS]

# Subscribe to all topics on the V3 bike
python -m das.mqtt_recorder /v3/#  -v

# Subscribe just BOOST and wireless module topics
python -m das.mqtt_recorder /v3/wireless-module/# power-model/# -v
```

| Flag                       |                          Info                           |
| :------------------------- | :-----------------------------------------------------: |
| `--host HOST`              |     Address of the MQTT broker (default: localhost)     |
| `-v ` or `--verbose`       |         Verbose logging output (default: False)         |
| `-t TIME` or `--time TIME` | Length of time to record data (duration) (default: inf) |
| `-h` or `--help`           |                          Help                           |



## [MQTT Playback](/DAS/das/mqtt_playback.py)
Once started this script will log any data coming in on the MQTT module data and battery channels. The saved csv files will be stored in the `das/csv_data`. 

### Usage
Within the poetry environment, run `python -m das.mqtt_wireless_logger --host 192.168.100.100`. This will connect to the MQTT broker set to 192.168.1.1000 and run a logger indefinitely. If no host is specified it will default to `localhost`.



## [Fake Module Tester](/DAS/das/utils/MockSensor.py.py)
This script mocks module data over MQTT similar to the real sensors on V3.

### Usage
Within the poetry environment, run `python -m das.tests.fake_module_tester --host 192.168.100.100 --time 10 --rate 2 --id 3`. This will run a fake test with the MQTT broker on 192.168.100.100 for 10 seconds, pinging out data 2 times per second only for module 3.






