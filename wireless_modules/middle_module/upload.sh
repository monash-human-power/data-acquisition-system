#!/bin/sh

# Note: Shell scripting should have no white space between the '=' operator for variable assigning

# declares an integer
declare -i BAUD_RATE=115200

PORT=$1
files="main.py ../config.py ../wireless_module.py  ../boot.py ../mqtt_client.py ../sensors/mpu.py \
../sensors/dht_sensor.py ../sensors/co2_sensor.py ../libraries/MQ135/mq135.py ../sensors/sensor_base.py \
../libraries/abc.py ../libraries/MPU6050-ESP8266-MicroPython/mpu6050.py"

# Check that the port name is specified in the argument
if [ $# -eq 0 ]
then   
    echo "Port name not specified after ./upload.sh command"
    exit 1
fi

# Function to upload file on ESP32
upload_file()
{
    # Parameters:
    # $1 (First argument to this function): The relative path of the file to upload

    # Place file on the board
    ampy -p $PORT -b $BAUD_RATE put $1

    # $? holds 0 if the last command executed ran successfully
    if [ $? == 0 ]
    then
        echo "$1 loaded"
    else
        echo "$1 NOT loaded"
    fi
}

# If there are more than 1 command line arguments, user has specified the files to upload in the arguments
if [ $# -gt 1 ]
then
    i=1
    # loop through each argument list and upload the file onto the board
    for arg
    do
        # If this is the first argument, ignore since it's the port name
        if [ $i -eq 1 ]
        then
            i=2

        else
            # Invoke function and pass arguments ($arg is the file name)
            upload_file $arg
        fi
    done

else
    # Upload all the default files listed under the files variable
    for file in $files
    do
        # Invoke function and pass $file as the argument
        upload_file $file
    done
fi

# Print black line at the end of execution
echo ""