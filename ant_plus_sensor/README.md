# Ant Plus Sensor

*This directory contains scripts to log the Ant-Plus sensors and send the data over MQTT*

## **[Ant-Plus Logger.js](https://github.com/monash-human-power/data-acquisition-system/blob/master/ant_plus_sensor/ant_plus_logger.js)**
`ant_plus_logger.js` is the only way we can communicate to ant+ devices. It serves as the middle-man between the ANT+ sensors and the DAS MQTT broker. It allows the sensors to show up as a virtual wireless sensor module.

## Getting Started

### Setting up node.js libraries
To install the necessary libraries for node.js you may need to manually install them instead of running `npm install`.

Run the script with `node ant_plus_logger.js`.

Sometimes, root permissions are required to connect to the USB dongle, so `sudo` may be required.

## Deployment

To start this script automatically, follow the instructions in [the services README.md](/services/README.md).

You will also need to ensure the default `pi` user has permissions to access the ANT+ dongle without `sudo`. Create the following file in `/etc/udev/rules.d/50-antplus.rules` and reboot:

```
# Allow access to ANT+ USB without sudo
# https://www.xmodulo.com/change-usb-device-permission-linux.html
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1008", GROUP="users", MODE="0666"
SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1009", GROUP="users", MODE="0666"
```

## Legacy Code
+ Teensy serial communication with the Ant+ can be found [here](https://github.com/monash-human-power/data-acquisition-system/blob/v2/Raspi/DAS.js)

+ Old Teensy scripts for collecting data can be found [here](https://github.com/monash-human-power/data-acquisition-system/tree/v2/Teensy)
