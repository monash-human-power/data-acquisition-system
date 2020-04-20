import pandas as pd 
import argparse 
from math import ceil
from numpy import median, mean

# averages data within the seconds, according to seconds array 
def avg_Data(array, technique):
    new_data = []

    if technique == "mean":
        for millisecond_indices in new_time:
            new_data_point = mean(array[millisecond_indices])
            new_data_point = round(new_data_point, ndigits=2)
            new_data.append(new_data_point)
    elif technique == "median":
        for millisecond_indices in new_time:
            new_data_point = median(array[millisecond_indices])
            new_data.append(new_data_point)

    return new_data

# accepts terminal commands
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input CSV file", action="store", required=True)
parser.add_argument("--output", help="Returns the filtered data", default="filtered_data.csv", action="store")
parser.add_argument("--unit", help="Specify time units (seconds, s, or minutes, m)", default="seconds", 
                    choices=["seconds", "s", "minutes", "m"], action="store")
parser.add_argument("--smooth", help="Smoothens data points by 3-point mean or median smoothing", 
                    choices=["mean","median"], default="mean", action="store")
args = parser.parse_args()

# initialising data
data = pd.read_csv(args.file)

milliseconds = data["time"]
gps_course = data["gps_course"]
gps_speed = data["gps_speed"]
tempC = data["thermoC"]
tempF = data["thermoF"]
cadence = data["cadence"]
power = data["power"]
reed_vel = data["reed_velocity"]
reed_dis = data["reed_distance"]

time = []
if args.unit == "seconds" or args.unit == "s":
    time = milliseconds/1000
elif args.unit == "minutes" or args.unit =="m":
    time = milliseconds/1000/60

# sorts time into specific time unit
new_time = []
previous_time = 0
for i in range(len(time)):
    if time[i] > previous_time:
        # sets new previous_time, pushes current millisecond_indices into seconds array, creates new millisecond_indices
        # millisecond_indices is an array of indexes for milliseconds within the same specified unit
        if previous_time != 0:
            # ignores first iteration
            new_time.append(millisecond_indices)

        previous_time = ceil(time[i])
        millisecond_indices = []

    # pushes index into current millisecond_indices
    millisecond_indices.append(i)

new_time.append(millisecond_indices)

# writes newly-manipulated data into new csv file
final = pd.DataFrame({
    "time": range(1, len(new_time)+1),
    "gps_course": avg_Data(gps_course, args.smooth),
    "gps_speed": avg_Data(gps_speed, args.smooth),
    "tempC": avg_Data(tempC, args.smooth),
    "tempF": avg_Data(tempF, args.smooth),
    "cadence": avg_Data(cadence, args.smooth),
    "power": avg_Data(power, args.smooth),
    "reed_velocity": avg_Data(reed_vel, args.smooth),
    "reed_distance": avg_Data(reed_dis, args.smooth)
})
final.to_csv(args.output, index=False)
