# DAS - Middle Wireless Module

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors)

The Middle Wireless Module allows us to collect and send data from the sensors attached to the bike. The middle wireless module consists of a micro controller (ESP32 currently) which gathers the data from the on board sensors and sends them using MQTT (over the internet).

This repository contains all the code related to Monash Human Power's middle wireless module - part of their Data Acquisition System (DAS).

## Getting Started

1. Create a local version of `config.py` in the same directory as the contents of this folder.
2. Your `config.py` should be similar to `config.example.py`. You'll need to replace the placeholders by the appropriate values.


## Uploading Code

```
# Change the first argument to the serial port of the ESP32, the second argument is the baud rate, which can be kept as it is.
./upload.sh /dev/ttyUSB0 115200
```

## Contents
- `main.py`: Processes messages and sends sensor data through MQTT


## Dependencies
- Ensure the `config.py` file is created locally (see the 'Getting Started' section above)
- The `test.py` requires the `paho-mqtt` library installed for Python


## Steps to test
1. Run the `boot.py` file to get your ESP32 connected to the WIFI (Find this in the `wireless_module` folder)
2. Run the `main.py` file and after starting it run the `test.py` file on your local computer and watch the console. The `test.py` can be found in the `wireless_module` folder.

