#!/bin/sh


printf "\nSending data csv file....\n\n"
source=$(printf "$(hostname)_$(date +%H-%M-%S)")
#scp /home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Pi_Data_v2a.csv pi@primary.local:/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Received_Data/$source.csv
scp /home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Pi_Data_v2a.csv pi@primary.local:/media/pi/PRIMARY/$source.csv
printf "\nData sent.\n\n"
