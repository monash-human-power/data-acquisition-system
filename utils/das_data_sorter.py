import pandas as pd 
import argparse 
from math import ceil

# accepts terminal commands
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input CSV file", action="store")
parser.add_argument("--output", help="Returns the filtered data", default="filtered_data.csv", action="store")
args = parser.parse_args()

# initialising data
data = pd.read_csv(args.file)
time = data["time"]/1000
gps_course = data["gps_course"]
gps_speed = data["gps_speed"]
tempC = data["thermoC"]
tempF = data["thermoF"]
cadence = data["cadence"]
power = data["power"]
reed_vel = data["reed_velocity"]
reed_dis = data["reed_distance"]

# sorts time into seconds
seconds = []
previous_time = 0
for i in range(len(time)):
    if time[i] > previous_time:
        # sets new previous_time, pushes current i_array into seconds array, creates new i_array
        # i_array is an array of indexes for milliseconds within the same second
        if previous_time != 0:
            #ignores first iteration
            seconds.append(i_array)

        previous_time = ceil(time[i])
        i_array = []

    # pushes index into current i_array
    i_array.append(i)
seconds.append(i_array)

# averages data within the seconds, according to seconds array 
def avgData(array):
    avg_array = []
    for second in seconds:
        total = 0
        for i in second:
            total = total + array[i]

        avg = round(total/len(second), ndigits=2)
        avg_array.append(avg)
    return avg_array

#writes newly-manipulated data into new csv file
final = pd.DataFrame({
    "time": range(1, len(seconds)+1),
    "gps_course": avgData(gps_course),
    "gps_speed": avgData(gps_speed),
    "tempC": avgData(tempC),
    "tempF": avgData(tempF),
    "cadence": avgData(cadence),
    "power": avgData(power),
    "reed_velocity": avgData(reed_vel),
    "reed_distance": avgData(reed_dis)
})
final.to_csv(args.output, index=False)
