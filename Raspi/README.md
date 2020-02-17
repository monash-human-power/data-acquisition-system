# Raspberry Pi Files
Scripts that are ran on the Raspberry Pi Zero W located on the DAS.

## Getting Started
### Installing node.js and npm on Raspberry Pi Zero W
*TBA*

### Setting up node.js libraries
To install the necessary libraries for node.js you may need to manually install them instead of running `npm install`.

#### Installing serialport (Windows)
Install required tools and configurations.
```
npm install --global --production windows-build-tools
```
Run the above command using an 'elevated PowerShell or CMD.exe (run as Administrator)'

Download `node-gyp`
```
$ npm install -g node-gyp
```

Install `serialport`
```
npm install serialport --build-from-source
```


#### Installing serialport (Raspberry Pi)

```
sudo npm install serialport --unsafe-perm --build-from-source
```
Running without the flags will lead to errors. See [this](https://github.com/node-serialport/node-serialport/tree/master/packages/serialport#raspberry-pi-linux) for more information about this.

## DAS Script
The DAS script serves as the middle-man between the ANT+ sensors and the DAS MQTT broker. It allows the sensors to show up as a virtual wireless sensor module.
