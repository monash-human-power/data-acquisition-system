# DAS

*This directory contains scripts to log and test various components of the data data-acquisition-system*

## **Basic Setup and Usage**
These steps assume that you are in the data-acquisition-system root directory.
1. `cd DAS`
2. `poetry install`
3. `poetry shell`
5. Run any DAS command, eg. `python -m das.mqtt_wireless_logger` (or `python mqtt_wireless_logger.py` as appropriate for your current directory)

<br>

## **[MQTT Wireless Logger](https://github.com/monash-human-power/data-acquisition-system/blob/master/DAS/das/mqtt_wireless_logger.py)**
Once started this script will log any data coming in on the MQTT module data and battery channels. The saved csv files will be stored in the `das/csv_data`. 

**Usage**: Within the poetry environment, run `python -m das.mqtt_wireless_logger --host 192.168.100.100`. This will connect to the MQTT broker set to 192.168.1.1000 and run a logger indefinitely. If no host is specified it will default to `localhost`.

<br>

## **[Fake Module Tester](https://github.com/monash-human-power/data-acquisition-system/blob/master/DAS/das/tests/fake_module_tester.py)**
This script mocks module data over MQTT similar to the real sensors on V3.

**Usage**: Within the poetry environment, run `python -m das.tests.fake_module_tester --host 192.168.100.100 --time 10 --rate 2 --id 3`. This will run a fake test with the MQTT broker on 192.168.100.100 for 10 seconds, pinging out data 2 times per second only for module 3.






