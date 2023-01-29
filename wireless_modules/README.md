# DAS Wireless Sensor Modules

Wireless sensor firmware based on MicroPython.

## Getting Started

For an overview of the wireless module usage from a user's view, see the [Notion manual](https://www.notion.so/Wireless-module-usage-manual-cd7e948418d040d991a50c91815e63e9).

### Set up development environment

Make sure to use Visual Studio Code for the best development experience.

```bash
# Install the required tools
pipenv install
pipenv shell

# Configure VS-Code auto-completion for micropython
micropy stubs add esp32-micropython-1.12.0
micropy
```

You will need to create a local version of `config.py` (`cp src/config.example.py src/config.py`) and change some settings.

| Name        | Description                        |
| ----------- | ---------------------------------- |
| MQTT_BROKER | IP address of the MQTT broker      |
| ESSID       | Name of WiFi network to connect to |
| PASSWORD    | WiFi password                      |

### Flashing MicroPython to the ESP32

The ESP32 needs to be flashed with the base micropython firmware. This only needs to be done once. See the [MicroPython ESP32 Getting Started guide](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html) for detailed instructions. At this point, version v1.13 of micropython (`esp32-idf3-20200902-v1.13.bin`) is required to run the modules. You can download the firmware [here](https://micropython.org/download/esp32/).

## Uploading Code
The `upload.sh` file in `middle_module` folder can be used to upload all relevant files on the ESP32.
```bash
# Change this to the serial port of the ESP32
./upload.sh --port /dev/ttyUSB0
```

## Running code on the ESP32
If using `picocom`:
1) Open terminal and connect the ESP32 to your computer
2) Run `picocom <insert_device_port_number> -b 115200`. This would run `boot.py` and then `main.py`.
3) Use `mosquitto` to interact with ESP32 (see [this](https://github.com/monash-human-power/data-acquisition-system/tree/master/wireless_modules/middle_module#steps-to-test))
4) If you find that the board is not publishing to the `mqtt` topic or is not running, try the next few steps.
5) Use `Control-C` to open REPL
6) To explicitly run a file, say `main.py` on the board use `import main.py` or `import main`, depending on your ESP32 version.
Note: This only works once in a `picocom` session, after that you'll need to close `picocom` and repeat from step 5.

Use `Control-A` and then `Control-X` to terminate `picocom`.
