# DAS - Middle Wireless Module

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors)

The Middle Wireless Module allows us to collect and send data from the sensors attached to the bike. The middle wireless module consists of a micro controller (ESP32 currently) which gathers the data from the on board sensors and sends them using MQTT (over the internet).

This repository contains all the code related to Monash Human Power's middle wireless module - part of their Data Acquisition System (DAS).

## Getting Started

1. Create a local version of `config.py` in the same directory as the contents of this folder.
2. Your `config.py` should be similar to `config.example.py`. You'll need to replace the placeholders by the appropriate values.


## Uploading Code

```
# Change the first argument to the serial port of the ESP32.
# This would upload all files relevant to this wireless module onto the board
./upload.sh /dev/ttyUSB0 

                            OR
                            
# To upload only specific files list their path after the port name argument
./upload.sh /dev/ttyUSB0 file1 ../file2 ... fileN
```

## Contents
- `main.py`: Declares topics to publish and subscribe to
- `upload.sh`: File to upload specific or all relevant files onto the ESP32 automatically 
- `test.py`: A python script to test the sensor data received from the middle wireless module over MQTT


## Dependencies
- Remember to run `git submodule update --init` to set up the required submodules
- Ensure the `config.py` file is created locally (see the 'Getting Started' section above)
- The `test.py` requires the `paho-mqtt` library installed for Python


## Steps to test
1. Run the `boot.py` file to get your ESP32 connected to the WIFI (Find this in the `wireless_module` folder)
2. Run the `main.py` file (Note: it would fail if the sensors are not connected and the script is run as it is)
3. Either run `test.py` file on your local computer to view the data received in a nicely formatted display or use the
    terminal on your system to send and receive data through `mosquitto`.
4. If using `mosquitto`, use 
    - `mosquitto_pub -h <broker name> -t /v3/wireless-module/2/start -m ""` to inform the module to start sending data
    - `mosquitto_pub -h <broker name> -t /v3/wireless-module/2/stop -m ""` to inform the module to stop sending data
    - `mosquitto_sub -h <broker name> -t /v3/wireless-module/2/data` to read data sent from the module

