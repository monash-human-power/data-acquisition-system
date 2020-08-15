#!/bin/sh
ampy -p $1 -b $2 put config.py
echo "config.py loaded"
ampy -p $1 -b $2 put main.py
echo "main.py loaded"
ampy -p $1 -b $2 put ../boot.py
echo "boot.py loaded"
ampy -p $1 -b $2 put ../mqtt_client.py
echo "mqtt_client.py loaded"
