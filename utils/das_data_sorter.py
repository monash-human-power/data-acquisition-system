import pandas as pd 
import argparse 
from math import ceil
from numpy import median, mean

# averages data within the seconds or minutes, according to new_time array
def avg_Data(array):
    avg_array = []

    for millisecond_indices in new_time:
        avg = mean(array[millisecond_indices])
        avg = round(avg, ndigits=2)
        avg_array.append(avg)

    return avg_array

# 3 point moving mean smoothing
def mean_smooth(data):
    new_data = []

    for i in range(1,len(data)-1):
        first = data[i-1]
        second = data[i]
        third = data[i+1]

        new_data_point = mean([first, second, third])
        new_data_point = round(new_data_point, ndigits=2)
        new_data.append(new_data_point)
    
    return new_data

# 3 point moving median smoothing
def median_smooth(data):
    new_data = []

    # iterates through each data point and its adjacents (excluding first and last) and finds the median 
    for i in range(1, len(data)-1):
        first = data[i-1]
        second = data[i]
        third = data[i+1]

        new_data_point = median([first, second, third])
        new_data.append(new_data_point)
    
    return new_data

# smoothing technique function caller
def smooth_data(data, technique):
    if technique == "mean":
        # when input is "--smooth mean"
        final_data = {
            "time": range(1, len(new_time)-1),
            "gps_course": mean_smooth(data["gps_course"]),
            "gps_speed": mean_smooth(data["gps_speed"]),
            "tempC": mean_smooth(data["tempC"]),
            "tempF": mean_smooth(data["tempF"]),
            "cadence": mean_smooth(data["cadence"]),
            "power": mean_smooth(data["power"]),
            "reed_velocity": mean_smooth(data["reed_velocity"]),
            "reed_distance": mean_smooth(data["reed_distance"])
        }
    elif technique == "median":
        # when input is "--smooth median"
        final_data = {
            "time": range(1, len(new_time)-1),
            "gps_course": median_smooth(data["gps_course"]),
            "gps_speed": median_smooth(data["gps_speed"]),
            "tempC": median_smooth(data["tempC"]),
            "tempF": median_smooth(data["tempF"]),
            "cadence": median_smooth(data["cadence"]),
            "power": median_smooth(data["power"]),
            "reed_velocity": median_smooth(data["reed_velocity"]),
            "reed_distance": median_smooth(data["reed_distance"])
        }
    
    return final_data

# averages data within the seconds, according to seconds array 
def avg_Data(array):
    avg_array = []

    for index_array in new_time:
        total = 0
        for index in index_array:
            total += array[index]

        avg = round(total/len(index_array), ndigits=2)
        avg_array.append(avg)
    return avg_array

# accepts terminal commands
parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Input CSV file", action="store", required=True)
parser.add_argument("--output", help="Returns the filtered data", default="filtered_data.csv", action="store")
parser.add_argument("--unit", help="Specify time units (seconds, s, or minutes, m)", default="seconds", 
                    choices=["seconds", "s", "minutes", "m"], action="store")

parser.add_argument("--smooth", help="Smoothens data points by 3-point mean or median smoothing", 
                    choices=["mean","median"], action="store")
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

# results of averaged data from milliseconds to seconds/minutes
new_avg_data = {
    "time": range(1, len(new_time)+1),
    "gps_course": avg_Data(gps_course),
    "gps_speed": avg_Data(gps_speed),
    "tempC": avg_Data(tempC),
    "tempF": avg_Data(tempF),
    "cadence": avg_Data(cadence),
    "power": avg_Data(power),
    "reed_velocity": avg_Data(reed_vel),
    "reed_distance": avg_Data(reed_dis)
}

# checks if user wants to smooth data using moving mean or moving median method
# if no input from user, script will ignore this whole block
if args.smooth == "mean":
    new_avg_data = smooth_data(new_avg_data, args.smooth)
elif args.smooth == "median":
    new_avg_data = smooth_data(new_avg_data, args.smooth)

# writes newly-manipulated data into new csv file
final = pd.DataFrame(new_avg_data)
final.to_csv(args.output, index=False)
