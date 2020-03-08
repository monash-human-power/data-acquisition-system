import pandas as pd 
from math import *

#initialising data
data = pd.read_excel("C:\\Users\JohnN\Documents\TheStuffOnHere\MHP\data_173.xlsx",sheet_name=0)
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

# checks if time in seconds is continuous
'''
new_time_array = []
previous_time2 =0
for time in time_array:
    if time > previous_time2:
        if previous_time2 !=0:
            #ignores first iteration
            seconds.append(i_array)

        previous_time2 = ceil(time)
        new_time_array.append(ceil(time))
print(new_time_array)
'''

# averages gps course
avg_course = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + gps_course[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_course.append(avg)
print(avg_course)

# averages gps speed
avg_speed = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + gps_speed[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_speed.append(avg)
print(avg_speed)

# averages temperature in celsius
avg_tempC = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + tempC[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_tempC.append(avg)
print(avg_tempC)

# averages temperature in farenheit
avg_tempF = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + tempF[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_tempF.append(avg)
print(avg_tempF)

# averages cadence
avg_cadence = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + cadence[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_cadence.append(avg)
print(avg_cadence)

# averages power
avg_power = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + power[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_power.append(avg)
print(avg_power)

# averages reed velocity
avg_reedV = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + reedV[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_reedV.append(avg)
print(avg_reedV)

# averages reed distance
avg_reedD = []
for i in range(len(seconds)):
    total = 0
    for j in seconds[i]:
        total = total + reedD[j]

    avg = round(total/len(seconds[i]), ndigits=2)
    avg_reedD.append(avg)
print(avg_reedD)
