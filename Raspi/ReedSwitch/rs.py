# Description: This file simply reads values from a reed switch. Given knowledge of the wheel size,
# and the time between readings, this script can calculate an estimate of speed.
# Last Modified: Thursday 12th July 2018 by Pat Graham
# Written By: Pat Graham

import os
import time			# For calculating times between reed switch triggers
import pigpio			# For handling reed switch input
import csv			# For storing reed switch data into a csv file

# This file makes use of pigpio to handle the gpio pins. The reason for this is sampling needs to take place at high speed. To set up pigpio on a new pi
# 1) Navigate to Other_Code/PIGPIO in this repo
# 2) Run "make -j4"
# 3) Run "sudo make install"
# 4) Open the /etc/rc.local file and place the command "sudo pigpiod" before the line "exit 0"
# 5) Reboot the pi

reed_pin = 18  		# GPIO pin for reed switch. Active low.
debug = 0     		# Prints the value of the reed switch. Useful for debugging.
Pi = 3.14159		# Value for pi.
d = 0.8			# diameter of the wheel
wait_for_reset = 1	# variable to monitor when to update speed as zero

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

    if(debug):
        print next

    # Only trigger when a falling edge is detected
    if next != previous and next == 0:
        next_time = time.time() 				# get the time at this instant
        time_delta = float(next_time - prev_time) 		# calculate time delta
        speed = (1.0 / time_delta) * Pi * d * 3.6 		# determine the speed using distance/time

        # Record data to a file
        with open(filename_velocity, "a") as csvfile:
            filewriter = csv.writer(csvfile)
            filewriter.writerow(["%.3f" % (next_time - start_time), "%.2f" % speed, "\n"])

        # Refresh the previous time
        prev_time = next_time

        wait_for_reset = 1

    # Refresh previous reed switch reed pin value before next loop
    previous = next

    # If nothing has happened in 3 seconds, record zero velocity
    if (wait_for_reset):
        if (time.time() - prev_time) > 3:
            wait_for_reset = 0
            with open(filename_velocity, "a") as csvfile:
                speed = 0
                filewriter = csv.writer(csvfile)
                filewriter.writerow(["%.5f" % (time.time() - start_time), "%.2f" % speed, "\n"])

    # End while loop here, repeat
