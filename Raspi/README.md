# Raspberry Pi Files
Scripts that are ran on the Raspberry Pi Zero W located on the DAS.

## Getting Started
### Installing node.js on Raspberry Pi Zero W
*TBA*

### Setting up node.js libraries
To install the necessary libraries for node.js you may need to manually install them instead of running `npm install`.

#### Installing serialport
```
sudo npm install serialport --unsafe-perm --build-from-source 
```
Running without the flags will lead to errors. See [this](https://github.com/node-serialport/node-serialport/tree/master/packages/serialport#raspberry-pi-linux) for more information about this.

## DAS Scripts
The DAS scripts (python and node.js) serves as the middle-man between the Teensy and the DAS web server. They enable the Teensy to send a string of data onto the Raspberry Pi which can then be used with these scripts and sent to the DAS web server.

The basic flow of the program is as follows:

1. Check if server is online every 1.5 seconds
2. When server is online, check if ant-plus dongle is connected
3. When ant-plus dongle is connected, open up serial port
3. Handle incoming data from serial port

There is currently a python and a node.js version. Note that the python version does not connect with the power meter.