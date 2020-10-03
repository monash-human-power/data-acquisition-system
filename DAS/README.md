# DAS

*This directory contains scripts to log and test various components of the data data-acquisition-system*



## Basic Setup and Usage
These steps assume that you are in the data-acquisition-system root directory.
1. `cd DAS`
2. `poetry install`
3. `poetry shell`
4. Run any DAS command, _e.g._ `python -m das.mqtt_recorder`

<br/>

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

<br/>

## [MQTT Playback](/DAS/das/mqtt_playback.py)
This command line tool reads a raw csv log created from the MQTT Recorder tool and plays it back over MQTT. Simply specify the log and this tool will do the rest!

### Usage
```
# General command
python -m das.mqtt_playback [FILEPATH] [FLAGS]

# Playback of 1_log.csv
python -m das.mqtt_playback ./das/csv_data/1_log.csv  -v

# Playback of 2_log.csv at 60x speed 
python -m das.mqtt_playback ./das/csv_data/2_log.csv -s 60 -v
```

| Flag                          |                      Info                       |
| :---------------------------- | :---------------------------------------------: |
| `--host HOST`                 | Address of the MQTT broker (default: localhost) |
| `-v ` or `--verbose`          |     Verbose logging output (default: False)     |
| `-s SPEED` or `--speed SPEED` |         Playback speed up (default: 1)          |
| `-h` or `--help`              |                      Help                       |

<br/>

## [Fake Module Tester](/DAS/das/utils/MockSensor.py.py)
This script mocks module data over MQTT similar to the real sensors on V3.

### Usage
Within the poetry environment, run `python -m das.tests.fake_module_tester --host 192.168.100.100 --time 10 --rate 2 --id 3`. This will run a fake test with the MQTT broker on 192.168.100.100 for 10 seconds, pinging out data 2 times per second only for module 3.






