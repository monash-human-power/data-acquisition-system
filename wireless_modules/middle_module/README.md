# DAS - Middle Wireless Module

[![All Contributors](https://img.shields.io/badge/all_contributors-6-orange.svg?style=flat-square)](#contributors)

The Middle Wireless Module allows us to collect and send data from the sensors attached to the bike. The middle wireless module consists of a micro controller (ESP32 currently) which gathers the data from the on board sensors and sends them using MQTT (over the internet).

This repository contains all the code related to Monash Human Power's middle wireless module - part of their Data Acquisition System (DAS).

## Getting Started

1. Create a local version of `config.py` in the same directory as the contents of this folder.
2. Your `config.py` should be similar to `config.example.py`. You'll need to replace the placeholders by the appropriate values.

## Contents
- `boot.py`: Contains functions to connect the microcontroller to the internet
- `main.py`: Processes MQTT messages and sends sensor data
- `mqtt_client.py`: Holds the Client class (used to work with MQTT)
- `test.py`: A python file (NOT Micropython) used to run on the local computer to test the `main.py` and `mqtt_class.py` files. It sends on the `/v3/wireless-module/<-id->/start` topic, to check whether it initiates the `main.py` file to send through the data on the topic `/v3/wireless-module/<-id->/data` and then send on the topic `/v3/wireless-module/<-id->/stop` to check whether it stops the inflow data. 
	- Note: There's some latency with MQTT and so after the stop topic is used the `test.py` finishes running and so may not print the last few data sent by `main.py`.
	- Also when running `test.py` if you do not receive any messages, re-run because most likely `main.py` was not ready to read the message from the start topic when it was sent by `test.py` (This may be due to some error and the need for the ESP32 to restart which would take some time)


## Dependencies
- The `test.py` requires the `paho-mqtt` library installed for Python
- The other `.py` files are Micropython files so needs a board to run on (eg ESP32)
- Ensure the `config.py` file is created locally (see the 'Getting Started' section above)


## Steps to test
1. Run the `boot.py` file to get your ESP32 connected to the WIFI
2. Run the `main.py` file and after starting it run the `test.py` file on your local computer and watch the console.
3. The `test.py` file allows `main.py` to send for 10-14 seconds (default).
4. Note that this process may take around 20 seconds (10 seconds for actual data sending and allowing for 10 seconds initially in case the ESP32 needs to reboot to reconnect to the MQTT broker)

