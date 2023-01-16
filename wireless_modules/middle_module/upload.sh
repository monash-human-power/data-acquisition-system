#!/bin/sh
# Purpose: To upload specific files or all relevant middle wireless module files (default) onto the ESP32
# Requirements: Must have ampy downloaded

# NOTE: 
# Shell scripting should have no white space between the '=' operator for variable assigning

# declares an integer
declare -i BAUD_RATE=115200

PORT=$1
NUM_ARGS=$#
files=(
    "main.py" 
    "../config.py" 
    "../wireless_module.py"
    "../boot.py"
    "../mqtt_client.py"
    "../sensors/sensor_base.py"
    "../sensors/mpu_sensor.py"
    "../sensors/dht_sensor.py"
    "../sensors/co2_sensor.py"
    "../libraries/abc.py"
    "../libraries/MQ135/mq135.py"
    "../libraries/MPU6050-ESP8266-MicroPython/mpu6050.py"
    "../battery_reader.py"
)

# Check that the port name is specified in the argument 
if [ $NUM_ARGS -eq 0 ]
then   
    echo "Port name not specified after ./upload.sh command"
    exit 1
fi

# Function to upload file onto the board
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
if [ $NUM_ARGS -gt 1 ]
then
    i=1
    # loop through each argument provided and upload the file given onto the board
    for arg
    do
        # If this is the first argument, ignore since it's the port name
        if [ $i -eq 1 ]
        then
            i=2

        else
            # Invoke function and pass file name as argument
            upload_file $arg
        fi
    done

else
    # Upload all the default files listed inside the files array
    for file in ${files[@]}
    do
        # Invoke function and pass $file as the argument
        upload_file $file
    done
fi

# Print black line at the end of execution for readability
echo ""
