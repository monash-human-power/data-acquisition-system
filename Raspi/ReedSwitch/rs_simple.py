# Description: This file simply reads values from a reed switch. Given knowledge of the wheel size,
# and the time between readings, this script can calculate an estimate of speed.
# Last Modified: Thursday 12th July 2018 by Pat Graham
# Written By: Pat Graham

import os
import time                     # For calculating times between reed switch triggers
import pigpio                   # For handling reed switch input
import csv                      # For storing reed switch data into a csv file

# This file makes use of pigpio to handle the gpio pins. The reason for this is sampling needs to take place at high speed. To set up pigpio on a new pi
# 1) Navigate to Other_Code/PIGPIO in this repo
# 2) Run "make -j4"
# 3) Run "sudo make install"
# 4) Open the /etc/rc.local file and place the command "sudo pigpiod" before the line "exit 0"
# 5) Reboot the pi

reed_pin = 18           # GPIO pin for reed switch. Active low.

pi = pigpio.pi()
pi.set_mode(reed_pin, pigpio.INPUT)
pi.set_pull_up_down(reed_pin, pigpio.PUD_UP)

# Set up Velocity file
i = 0
while os.path.exists("/home/pi/Documents/MHP_DAS/Raspi/ReedSwitch/Recording_%s.csv" % i):
    i += 1
filename_velocity = "/home/pi/Documents/MHP_DAS/Raspi/ReedSwitch/Recording_%s.csv" % i

# Initialize loop variables
previous = pi.read(reed_pin)
prev_time = time.time()
start_time = time.time()

while  True:

    # Find the next reed pin read
    next = pi.read(reed_pin)

    # Only trigger when a falling edge is detected
    if next != previous and next == 0:
        next_time = time.time()                                 # get the time at this instant
        time_delta = float(next_time - prev_time)               # calculate time delta

        # Record data to a file
        with open(filename_velocity, "a") as csvfile:
            filewriter = csv.writer(csvfile)
            filewriter.writerow(["%.3f" % (next_time - start_time)])

        # Refresh the previous time
        prev_time = next_time

    # Refresh previous reed switch reed pin value before next loop
    previous = next

    # End while loop here, repeat


