# Ant Plus Sensor

*This directory contains scripts to log the Ant-Plus sensors and send the data over MQTT*

## **[Ant-Plus Logger.js](https://github.com/monash-human-power/data-acquisition-system/blob/master/ant_plus_sensor/ant_plus_logger.js)**
`ant_plus_logger.js` is the only way we can communicate to ant+ devices. It serves as the middle-man between the ANT+ sensors and the DAS MQTT broker. It allows the sensors to show up as a virtual wireless sensor module.

## **Getting Started**

### Setting up node.js libraries
To install the necessary libraries for node.js you may need to manually install them instead of running `npm install`.

## **Legacy Code**
+ Teensy serial communication with the Ant+ can be found [here](https://github.com/monash-human-power/data-acquisition-system/blob/v2/Raspi/DAS.js)

+ Old Teensy scripts for collecting data can be found [here](https://github.com/monash-human-power/data-acquisition-system/tree/v2/Teensy)
