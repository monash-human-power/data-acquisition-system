# MQTT Radio Bridge


## Installation

1. If you did not clone submodules when cloning, run
    ```bash
    git submodule update --init
    ```
2. Download and install the Paho MQTT C library with (this can be done from any folder)
    ```bash
    git clone https://github.com/eclipse/paho.mqtt.c.git
    cd paho.mqtt.c
    git checkout v1.3.1

    cmake -Bbuild -H. -DPAHO_WITH_SSL=ON -DPAHO_ENABLE_TESTING=OFF
    sudo cmake --build build/ --target install
    sudo ldconfig
    ```
3. `cd` back to this `Bridge` directory, and run the following to configure and build.
    ```bash
    cmake .
    make
    ```