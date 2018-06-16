#!/bin/bash

inputMAC=$1

# Scan Criteria (Based on Router dhcp allocation range)
start_ip=192.168.1.100
ip_scan_range=10

# Prepare for loop
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
        MAC=$(arp -n $addr | awk 'FNR == 2 {print $3}')
	if [ -z "$MAC" ]
	then
		lsv=$(( $lsv + 1 )) # Increment lower end of ip address count
    		ip_scan_range=$(( $ip_scan_range - 1 )) # decrement ip address scan range
		continue
	fi
	
	## Notify host has been found
        #printf "\nFound Active Host\n"
        #printf "MAC Address = $MAC\n" # Print MAC Address
	#printf "IP Address = $addr\n" # Print MAC Address
	
        # Check to see if MAC Address is one of list of known Pi's.
        if [ "$MAC" == "$inputMAC" ]
        then
            #printf "Found Target Pi\n"
	    printf "$addr"
	    exit 
	fi
    fi
    lsv=$(( $lsv + 1 )) # Increment lower end of ip address count
    ip_scan_range=$(( $ip_scan_range - 1 )) # decrement ip address scan range
done

printf "0"
exit 0