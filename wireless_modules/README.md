# DAS Wireless Sensor Modules

Wireless sensor firmware based on MicroPython.

## Getting Started

### Set up development environment

Make sure to use Visual Studio Code for the best development experience.

```
# Install the required tools
pipenv install
pipenv shell

# Configure VS-Code auto-completion for micropython
micropy stubs add esp32-micropython-1.12.0
micropy
```

You will need to create a local version of `config.py` (`cp src/config.example.py src/config.py`) and change some settings.

|Name|Description|
|----|-----------|
|SENSOR_ID|Wireless module ID|
|WIFI_SSID|Name of Wifi network to connect to|
|WIFI_PASS|Wifi password|

### Flashing MicroPython to the ESP32

The ESP32 needs to be flashed with the base micropython firmware. This only needs to be done once. See the [MicroPython ESP32 Getting Started guide](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) for detailed instructions.

## Uploading Code

```
# Change this to the serial port of the ESP32
./upload.sh --port /dev/ttyUSB0
```

## TODOs

*To remove once you have everything done!*

- [x] `.env` file
- [ ] Linters
- [ ] travisCI files
- [ ] Badges
- [ ] Linting hooks
- [ ] Basic unit tests
- [x] Set `master` branch protection. Only allow Squash and Merge for PR's. At least 1 approval.