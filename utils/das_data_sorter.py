import pandas as pd 
import argparse 
from math import *

#accepts terminal commands
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input CSV file", action="store")
parser.add_argument("--output", help="Returns the filtered data", default="filtered_data.csv", action="store")
args = parser.parse_args()

#initialising data
data = pd.read_csv(args.file)
time_array = data['time']/1000
gps_course = data['gps_course']
gps_speed = data['gps_speed']
tempC = data['thermoC']
tempF = data['thermoF']
cadence = data['cadence']
power = data['power']
reedV = data['reed_velocity']
reedD = data['reed_distance']

# sorts data into seconds
seconds = []
previous_time = 0
for i in range(len(time_array)):
    if time_array[i] > previous_time:
        # sets new previous_time, pushes current i_array into seconds array, creates new i_array
        if previous_time !=0:
            #ignores first iteration
            seconds.append(i_array)

        previous_time = ceil(time_array[i])
        i_array = []
        i_array.append(i)
    else:
        # pushes index into current i_array, if not greater than previous_time
        i_array.append(i)
seconds.append(i_array)

# averages data
def avgData(array):
    avg_array = []
    for second in seconds:
        total=0
        for i in second:
            total = total + array[i]

        avg = round(total/len(second), ndigits=2)
        avg_array.append(avg)
    return avg_array

#writes newly-manipulated data into new csv file
final = pd.DataFrame({
    'time':range(1, len(seconds)+1),
    'gps_course':avgData(gps_course),
    'gps_speed':avgData(gps_speed),
    'tempC':avgData(tempC),
    'tempF':avgData(tempF),
    'cadence':avgData(cadence),
    'power':avgData(power),
    'reed_velocity':avgData(reedV),
    'reed_distance':avgData(reedD)
})
final.to_csv(args.output, index=False)
