import pandas as pd 
from math import *

data = pd.read_excel("C:\\Users\JohnN\Documents\TheStuffOnHere\MHP\das_data_sorter\data_173.xlsx",sheet_name=1)
time = data['time']
print(time)

# sorts data into seconds
seconds = []
for i in range(len(time)):
    previous_time = 0
    if time[i]/1000 > previous_time:
        #pushes current array of indexes into seconds array, updates previous_time variable, and creates a new array of indexes
        if previous_time != 0:
            #excludes first time value
            seconds.append(time_index)

        previous_time = ceil(time[i]/1000)
        time_index = []
        time_index.append(i)
    else:
        #adds to current array
        time_index.append(i)

print(seconds)
