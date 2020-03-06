import pandas as pd 
from math import *

data = pd.read_excel("C:\\Users\JohnN\Documents\TheStuffOnHere\MHP\data_173.xlsx",sheet_name=1)
time_array = data['time']/1000

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
print(seconds)

# nested for loop for future reference when iterating through each "second"
for i in range(len(seconds)):
    for j in range(len(seconds[i])):
        print(time_array[seconds[i][j]])
    print("one second")
