# ---------------------------------------------------------------------
# Last Modified:
#   9-12-2017
# Description:
#   This program reads data from the accelerometer and dumps
#   it to a csv file. It is important to keep this file short as
#   speed of execution is critical.
# ---------------------------------------------------------------------

# ---------------------- Import required libraries --------------------
import IMUv2a
import time
import math
import csv

# ---------------------- Initialise berryIMU --------------------------
IMUv2a.detectIMU()
IMUv2a.initIMU()  # Initialise the accelerometer, gyroscope and compass

# ---------------------- Start Program --------------------------------

# Open file to print too

filename = "/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Pi_Data_v2a.csv"
file = open(filename, 'w')
filewrite = csv.writer(file, delimiter=',', lineterminator='\n')

# Record program start time
init_time = time.time()

while True:
    try:
        # Read our accelerometer,gyroscope and magnetometer  values
        ACCx = IMUv2a.readACCx()
        ACCy = IMUv2a.readACCy()
        ACCz = IMUv2a.readACCz()

        # Record time when i2c read ends, calculate difference
        time_elapsed = round(time.time() - init_time, 5)

        # Write information to file
        filewrite.writerow([time_elapsed, ACCx, ACCy, ACCz])

    except KeyboardInterrupt:
        # End program
        file.close()
        break
