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
milliseconds = data["time"]/1000
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
for i in range(len(milliseconds)):
    if milliseconds[i] > previous_time:
        # sets new previous_time, pushes current millisecond_indices into seconds array, creates new millisecond_indices
        # millisecond_indices is an array of indexes for milliseconds within the same second
        if previous_time != 0:
            #ignores first iteration
            seconds.append(millisecond_indices)

        previous_time = ceil(time[i])
        millisecond_indices = []

    # pushes index into current millisecond_indices
    millisecond_indices.append(i)
seconds.append(millisecond_indices)

# averages data within the seconds, according to seconds array 
def avg_Data(array):
    avg_array = []
    for second in seconds:
        total = 0
        for i in second:
            total += array[i]

        avg = round(total/len(second), ndigits=2)
        avg_array.append(avg)
    return avg_array

# writes newly-manipulated data into new csv file
final = pd.DataFrame({
    "time": range(1, len(seconds)+1),
    "gps_course": avg_Data(gps_course),
    "gps_speed": avg_Data(gps_speed),
    "tempC": avg_Data(tempC),
    "tempF": avg_Data(tempF),
    "cadence": avg_Data(cadence),
    "power": avg_Data(power),
    "reed_velocity": avg_Data(reed_vel),
    "reed_distance": avg_Data(reed_dis)
})
final.to_csv(args.output, index=False)
