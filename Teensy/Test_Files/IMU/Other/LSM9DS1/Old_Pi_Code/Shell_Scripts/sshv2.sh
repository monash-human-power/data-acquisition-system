#!/bin/bash

# This script automates ssh connection using the network ping utility. It is
# appropriate only when a pi is attempting to connect to Telstra 4G USB Modem.
# It should not be used in any other scenario.

# Known and recognised Target Pi's.
USERNAME=pi # all pi's have same username
PatMacbookMAC=6c:40:8:99:ce:b0
PatPiMAC=b8:27:eb:d0:ac:d8
PiZero1MAC=b8:27:eb:3b:26:bb
PiZero2MAC=b8:27:eb:19:78:4c
PiZero3MAC=b8:27:eb:f:69:e5
PiZero4MAC=b8:27:eb:5f:91:1a
PiZero5MAC=b8:27:eb:3c:c9:14
PiZero6MAC=b8:27:eb:21:f0:52
PiPrimaryMAC=b8:27:eb:cb:70:a1
PiSecondaryMAC=b8:27:eb:85:52:20

# Select Target Pi (either manually or through user input)
#TargetPi = 1 # Assign manually in script
printf "\nKNOWN PI'S";
printf "\n\tName:\t\tID:"

printf "\n\tPat Pi\t\t0"
printf "\n\tPi Zero 1\t1"
printf "\n\tPi Zero 2\t2"
printf "\n\tPi Zero 3\t3"
printf "\n\tPi Zero 4\t4"
printf "\n\tPi Zero 5\t5"
printf "\n\tPi Zero 6\t6"
printf "\n\tPrimary\t\t7"
printf "\n\tSecondary\t8\n"

printf "\nSelect target Pi ID = "; read TargetPi # Read from user input

# Choose MAC Address to Search for
if [ $TargetPi == 0 ]
then
    SearchMAC=$PatPiMAC
elif [ $TargetPi == 1 ]
then
    SearchMAC=$PiZero1MAC
elif [ $TargetPi == 2 ]
then
    SearchMAC=$PiZero2MAC
elif [ $TargetPi == 3 ]
then
    SearchMAC=$PiZero3MAC
elif [ $TargetPi == 4 ]
then
    SearchMAC=$PiZero4MAC
elif [ $TargetPi == 5 ]
then
    SearchMAC=$PiZero5MAC
elif [ $TargetPi == 6 ]
then
    SearchMAC=$PiZero6MAC
elif [ $TargetPi == 7 ]
then
    SearchMAC=$PiPrimaryMAC
elif [ $TargetPi == 8 ]
then
    SearchMAC=$PiSecondaryMAC
fi

# Scan Criteria (Based on Router dhcp allocation range)
start_ip=192.168.1.100
ip_scan_range=10

# Prepare for loop
ssh=0 # do not initiate ssh connection
baseaddr="$(echo $start_ip | cut -d. -f1-3)"
lsv="$(echo $start_ip | cut -d. -f4)"

# Scan for Pi
while [ $ip_scan_range -gt 0 ] # Terminate loop when scan range == 0
do
    # Increment scan ip address
    addr="$(echo $baseaddr.$lsv)"

    # Ping that address to check for host
    fping=$(fping -c 1 -t 500 $addr 2>/dev/null | sort)

    # If ping returns non-empty information, host is online
    if [ ! -z "$fping" ]
    then
        # Notify host has been found
        printf "\nFound Active Host\n"

        # Find the MAC address associated with that IP Address
        MAC=$(arp -n $addr | awk '{print $4}')
        printf "MAC Address = $MAC\n" # Print MAC Address

        # Check to see if MAC Address is one of list of known Pi's.
        if [ "$MAC" == "$PatPiMAC" ]
        then
            printf "Found Pat Pi\n"
        elif [ "$MAC" == $PiZero1MAC ]
        then
            printf "Found Pi Zero 1\n"
        elif [ "$MAC" == $PiZero2MAC ]
        then
            printf "Found Pi Zero 2\n"
        elif [ "$MAC" == $PiZero3MAC ]
        then
            printf "Found Pi Zero 3\n"
        elif [ "$MAC" == $PiZero4MAC ]
        then
            printf "Found Pi Zero 4\n"
        elif [ "$MAC" == $PiZero5MAC ]
        then
            printf "Found Pi Zero 5\n"
        elif [ "$MAC" == $PiZero6MAC ]
        then
            printf "Found Pi Zero 6\n"
        elif [ "$MAC" == $PiPrimaryMAC ]
        then
            printf "Found Primary Pi\n"
        elif [ "$MAC" == $PiSecondaryMAC ]
        then
            printf "Found Secondary Pi\n"
        elif [ "$MAC" == $PatMacbookMAC ]
        then
            printf "Found Pat's Macbook\n"
        fi

        # Check to see if MAC Address is that of Target Pi
        if [ "$MAC" == "$SearchMAC" ]
        then
            ssh=1 # initiate ssh connection once exited loop
            PI_IP=$addr # assign ssh IP Address
            printf "Target Pi Found @ $PI_IP\n" # Notify found target pi
            break #break from loop
        fi
    fi
    lsv=$(( $lsv + 1 )) # Increment lower end of ip address count
    ip_scan_range=$(( $ip_scan_range - 1 )) # decrement ip address scan range
done

# If statement will be activated if target pi is found
if [ $ssh == 1 ]
then
    printf "\nStarting ssh connection @ $PI_IP...\n\n"
    ssh -o StrictHostKeyChecking=no ${USERNAME}@${PI_IP} # SSH session begins
else
    printf "\nFailed to find target Pi. Check to see if Pi is online.\n"
fi

printf "\n" # add new line for neatness
exit 0 # end of program

## Code when looking for just any Pi
#TempMAC=$(echo $MAC |rev|cut -d":" -f4-|rev)
#echo "MAC Address begins with $TempMAC"
