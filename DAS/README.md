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

## [Fake Module](/DAS/das/fake_module.py)
This script mocks module data over MQTT similar to the real sensors on V3.

### Usage
```
# General command
python -m das.fake_module [FLAGS]

# Fake sensor output for 10s at 3 messages per second
python -m das.fake_module -t 10 -r 3

# Fake sensor output for just module 1 and 2
python -m das.fake_module --id 1 2
```

| Flag                                    |                               Info                               |
| :-------------------------------------- | :--------------------------------------------------------------: |
| `--host HOST`                           |         Address of the MQTT broker (default: localhost)          |
| `-t TIME` or `--time TIME`              |     Length of time to record data (duration) (default: inf)      |
| `-r RATE` or `--rate RATE`              |            Rate of data sent per second (default: 1)             |
| ` -i ID [ID ...]` or `--id ID [ID ...]` | Specify the modules to produce fake data (default: [1, 2, 3, 4]) |
| `-h` or `--help`                        |                               Help                               |




