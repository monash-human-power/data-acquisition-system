#!/bin/sh

# Check that the port name is specified in the argumennt
if [ $# -eq 0 ]
then   
    echo "Port name not specified after ./upload.sh command"
    exit 1
fi

# Shell scripting should have no white space between the '=' operator for variable asisgning

# declares an integer
declare -i BAUD_RATE=115200

files="config.py ../wireless_module.py"

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

