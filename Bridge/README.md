# MQTT Radio Bridge


## About

This program is used to join (or "bridge") the two MQTT brokers on the bike and the chase car so that MQTT messages may be sent without relying on being on the same local network.

At a high level, this works by making a subscription to all MQTT topics (`#`), and then for each received message:

1. Check the message was not one that was sent by the bridge itself (performed in the `Bridge` class),
2. Serialise the message into a series of bytes (performed in the `TxProtocol` class),
3. Pack the bytes into one or more `Frame`s, or radio packets (also `TxProtocol`),
4. Send each of the `Frame`s over the radio (using `ZetaRfRadio`).

On the other end of the bridge, the reverse process would happen.

5. A packet is received by `ZetaRfRadio`,
6. It is processed by `RxProtocol`, which will emit create a MQTT message when enough packets have arrived,
7. `Bridge` will register the message as one sent by the MQTT radio bridge, before finally,
8. The MQTT message is published using `MqttBridgeClient`.

Details on the protocol used for converting an MQTT message into bytes, and then into packets may be found on Notion.

### Radio configuration

Radio configurations are stored in `src/rf_config`.
The `.xml` file is for use in Silicon Labs' [EZRadio Wireless Development Suite](https://www.silabs.com/products/development-tools/software/wireless-development-suite), which outputs a header file which is easily modified into the existing `.h` and `.cpp` files in the same directory.

## Installation

1. If you did not clone submodules when cloning, run
    ```bash
    git submodule update --init
    ```
2. Install `wiringpi`:
   ```bash
   sudo apt install wiringpi
   ```
3. Download and install the Paho MQTT C library with (this can be done from any folder)
    ```bash
    git clone https://github.com/eclipse/paho.mqtt.c.git
    cd paho.mqtt.c
    git checkout v1.3.1

    cmake -Bbuild -H. -DPAHO_WITH_SSL=ON -DPAHO_ENABLE_TESTING=OFF
    sudo cmake --build build/ --target install
    sudo ldconfig
    ```
4. `cd` back to this `Bridge` directory, and run the following to configure and build.
    ```bash
    cmake .
    cmake --build . --config Release
    ```
    If lots of debug messages are desired, then `Release` may be relpaced with `Debug`.
    This will, amongst other things, print the bytes of every message sent or received.

## Usage

You will need to have this repo installed on two Raspberry Pis.

On both Pis, once built (see above), start the executable with `./build/ZetaBridge`.

Note: Currently, there are no configuration options for this project.
If you wish to change the MQTT broker IP address, you must do so manually inside `mqtt.cpp`.
By default, the client will connect to `tcp://localhost:1883`.
