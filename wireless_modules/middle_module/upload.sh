#!/bin/sh
ampy -p $1 -b 115200 put ../config.py
echo "config.py loaded"
ampy -p $1 -b 115200 put main.py
echo "main.py loaded"
ampy -p $1 -b 115200 put ../boot.py
echo "boot.py loaded"
ampy -p $1 -b 115200 put ../mqtt_client.py
echo "mqtt_client.py loaded"
