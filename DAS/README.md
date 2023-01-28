# DAS

*This directory contains scripts to log and test various components of the data-acquisition-system*


- [DAS](#das)
  - [Basic Setup and Usage](#basic-setup-and-usage)
  - [Unit Tests](#unit-tests)
  - [V3 MQTT Recorder](#v3-mqtt-recorder)
    - [Usage](#usage)
  - [V3 MQTT Playback](#v3-mqtt-playback)
    - [Usage](#usage-1)
  - [V3 Fake Module](#v3-fake-module)
    - [Usage](#usage-2)
  - [V2 MQTT Playback](#v2-mqtt-playback)
    - [Usage](#usage-3)
  - [Log to Excel](#log-to-excel)
    - [Setup] (#setup)
    - [Usage](#usage-4)


## Basic Setup and Usage
These steps assume that you have [poetry](https://python-poetry.org/) installed.

```bash
# Move into DAS directory
cd DAS

# Install dependencies using poetry
poetry install

# Enter into poetry shell [OPTIONAL] 
poetry shell
```

## Unit Tests

```bash
poetry run pytest
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

| Flag                       | Default Value |                        Info                         |
| :------------------------- | :-----------: | :-------------------------------------------------: |
| `--host HOST`              |  `localhost`  |             Address of the MQTT broker              |
| `-v ` or `--verbose`       |    `False`    |               Verbose logging output                |
| `-t TIME` or `--time TIME` |     `inf`     | Length of time to record data (duration in seconds) |
| `--username USERNAME`      |    `None`     |            Username for the MQTT broker             |
| `--password PASSWORD`      |    `None`     |            Password for the MQTT broker             |
| `-h` or `--help`           |               |                        Help                         |

<br/>

## [V3 MQTT Playback](/DAS/das/V3_mqtt_playback.py)
This command line tool reads a sqlite database file created from the V3 MQTT Recorder tool and plays it back over MQTT. Simply specify the database file and this tool will do the rest!

### Usage
```bash
# General command
poetry run python -m das.V3_mqtt_playback [FLAGS]

# Playback of all logs
poetry run python -m das.V3_mqtt_playback -v

# Playback of all logs at 60x speed 
poetry run python -m das.V3_mqtt_playback -s 60 -v
```

| Flag                          | Default Value |               Info               |
| :---------------------------- | :-----------: | :------------------------------: |
| `--host HOST`                 |  `localhost`  |    Address of the MQTT broker    |
| `-v ` or `--verbose`          |    `False`    |      Verbose logging output      |
| `-s SPEED` or `--speed SPEED` |      `1`      | Playback speed up (x multiplier) |
| `--username USERNAME`         |    `None`     |   Username for the MQTT broker   |
| `--password PASSWORD`         |    `None`     |   Password for the MQTT broker   |
| `-h` or `--help`              |               |               Help               |

<br/>

## [V3 Fake Module](/DAS/das/V3_fake_module.py)
This script mocks module data over MQTT similar to the real sensors on V3.

### Usage
```bash
# General command
poetry run python -m das.V3_fake_module [FLAGS]

# Fake sensor output for 10s at 3 messages per second
poetry run python -m das.V3_fake_module -t 10 -r 3

# Fake sensor output for just module 1 and 2
poetry run python -m das.V3_fake_module --id 1 2
```

| Flag                                    | Default Value  |                        Info                         |
| :-------------------------------------- | :------------: | :-------------------------------------------------: |
| `--host HOST`                           |  `localhost`   |             Address of the MQTT broker              |
| `-t TIME` or `--time TIME`              |     `inf`      | Length of time to record data (duration in seconds) |
| `-r RATE` or `--rate RATE`              |      `1`       |            Rate of data sent per second             |
| ` -i ID [ID ...]` or `--id ID [ID ...]` | `[1, 2, 3, 4]` |      Specify the modules to produce fake data       |
| `-h` or `--help`                        |                |                        Help                         |

<br/>

## [V2 MQTT Playback](/DAS/das/V2_mqtt_playback.py)
This command line tool plays back MQTT data by reading a V2 csv log or making up fake data.

### Usage
```bash
# General command (with file)
poetry run python -m das.V2_mqtt_playback --file [FILEPATH] [FLAGS]

# General command (without file)
poetry run python -m das.V2_mqtt_playback [FLAGS]

# Playback of 1_log.csv for 30 seconds
poetry run python -m das.V2_mqtt_playback ./das/V2_csv_data/1_log.csv -t 30

# Playback of 2_log.csv at 60x speed 
poetry run python -m das.V2_mqtt_playback ./das/V2_csv_data/2_log.csv -s 60 
```

| Flag                          | Default Value |                           Info                           |
| :---------------------------- | :-----------: | :------------------------------------------------------: |
| `-t TIME` or `--time TIME`    |      `1`      |         Length of time to send data (in seconds)         |
| `-r RATE` or `--rate RATE`    |     `0.5`     |                  Rate of data (seconds)                  |
| `--host HOST`                 |  `localhost`  |                Address of the MQTT broker                |
| `--port PORT`                 |    `1883`     |                 Port of the MQTT broker                  |
| `--username USERNAME`         |               |               Username for the MQTT broker               |
| `--password PASSWORD`         |               |               Password for the MQTT broker               |
| `-f FILE` or `--file FILE`    |               | The csv file to replay (if not specified, makes up data) |
| `-s SPEED` or `--speed SPEED` |      `1`      |               Replay speed (x multiplier)                |
| `-j JUMP` or `--jump JUMP`    |      `0`      |   Starts replaying from a specified time (in seconds)    |

<br/>

## [Log to Excel](/DAS/das/log_2_excel.py)
This command line tool logs MQTT data into an SQLite database and converts these into excel files.

### Setup
The environment file needs to be setup correctly to ensure files are saved to the correct location.

```bash
#On your local device it should be the environment path that leads to these files
MQTT_LOG_FILE="PATH_TO/data-acquisition-system/DAS/das/sqlite/"
EXCEL_LOG_FILE="PATH_TO/dashboard/server/data/"
```

### Usage
```bash
# General command
poetry run python [FILEPATH] [FLAGS]

```

| Flag                                    | Default Value |                           Info                           |
| :-------------------------------------- | :-----------: | :------------------------------------------------------: |
| `--host HOST`                           |  `localhost`  |                Address of the MQTT broker                |
| `-v VERBOSE` or `--verbose VERBOSE`     |    `false`    |                 Verbose logging output                   |
| `-u USERNAME` or `--username USERNAME`  |               |               Username for the MQTT broker               |
| `-p PASSWORD` or `--password PASSWORD`  |               |               Password for the MQTT broker               |
| `-f FILENAME` or `--filename FILENAME`  |   `runfile`   |           File naming system for excel conversion        |
