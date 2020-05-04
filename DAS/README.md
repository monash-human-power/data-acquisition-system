# DAS

This directory contains scripts to log and test the data data-acquisition-system 

### Test/serial_test.py
Imitates the Teensy serial connection by creating a virtual serial port. Note that this will only work on Unix systems - if you're running Windows, perhaps try running the script under [Windows Subsystem for Linux (WSL)](https://docs.microsoft.com/en-us/windows/wsl/install-win10).

Usage: This script uses the same arguments as `mqtt_test.py`. For example, run the script with `python serial_test.py -f data_173.csv -j 1500`. The script will provide you with a serial port address. Run the DAS script with `node DAS.js -a -p [serial port]`. Return to the `serial_test` terminal, and press enter to begin sending data.

### Test/mock_wireless_module.py
This script mocks module data over MQTT similar to the real sensors on V3.

#### Usage: Common use cases for mocking modules (All flags can be used with each other)
- Send data once per second for 5 seconds for modules 1, 2, 3 and 4
  - `python3 mock_wireless_module.py -t 5`
- Send data five times per second for a minute for modules 1, 2, 3 and 4
  - `python3 mock_wireless_module.py -t 60 -r 5 `
- Send data once per second for modules 2, 5, and 1000 forever
  - `python3 mock_wireless_module.py -i 2 5 1000`
- Send data once per second for modules 1, 2, 3 and 4 for host on 192.168.1.100 forever
  - `python3 mock_wireless_module.py --host 192.168.1.100`


### Test/mqtt_wireless_log.py
Once started this script will log any data coming in on the MQTT module data and battery channels. The saved csv files will be in the format `module_id + _D%d-%m-%d_T%H-%M-%S + .csv`, where the date and time is the time when the start topic gets data sent on it.

#### Usage: Just start the script and data will be auto logged
- General use with the default MQTT broker set to localhost
  - `python3 mqtt_wireless_log.py`
- Same logger with the MQTT broker set to 192.168.1.100
  - `python3 mqtt_wireless_log.py --host 192.168.1.100`