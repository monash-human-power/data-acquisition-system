#!/bin/sh

# Note: Shell scripting should have no white space between the '=' operator for variable assigning

# Check that the port name is specified in the argument
if [ $# -eq 0 ]
then   
    echo "Port name not specified after ./upload.sh command"
    exit 1
fi


# declares an integer
declare -i BAUD_RATE=115200

files="main.py ../config.py ../wireless_module.py  ../boot.py ../mqtt_client.py ../sensors/mpu.py \
../sensors/dht_sensor.py ../sensors/co2_sensor.py ../libraries/MQ135/mq135.py ../sensors/sensor_base.py \
../libraries/abc.py ../libraries/MPU6050-ESP8266-MicroPython/mpu6050.py"

for file in $files
do 
    # Places file on the ESP32
    ampy -p $1 -b $BAUD_RATE put $file

    # '$?' stores 0 if the above command ran successfully
    if [ $? == 0 ]
    then
        echo "$file loaded"
    else
        echo "$file NOT loaded"
    fi
done
