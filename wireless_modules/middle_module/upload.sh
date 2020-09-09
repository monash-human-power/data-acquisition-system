#!/bin/sh
ampy -p $1 -b 115200 put ../config.py
echo "config.py loaded"
ampy -p $1 -b 115200 put main.py
echo "main.py loaded"
ampy -p $1 -b 115200 put ../boot.py
echo "boot.py loaded"
ampy -p $1 -b 115200 put ../mqtt_client.py
echo "mqtt_client.py loaded"
ampy -p $1 -b 115200 put ../wireless_module.py
echo "wireless_module.py loaded"
ampy -p $1 -b 115200 put MPU6050-ESP8266-MicroPython/mpu6050.py
echo "mpu6050.py loaded"
ampy -p $1 -b 115200 put mpu.py
echo "mpu.py loaded"
ampy -p $1 -b 115200 put ../common_sensors/dht_sensor.py
echo "dht_sensor.py loaded"
ampy -p $1 -b 115200 put ../common_sensors/mq135_sensor.py
echo "mq135_sensor.py loaded"
ampy -p $1 -b 115200 put ../MQ135/mq135.py
echo "mq135.py loaded"