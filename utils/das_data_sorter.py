import pandas as pd 
from argparse import ArgumentParser
from numpy import ceil, median

# accepts terminal arguments
parser = ArgumentParser()
parser.add_argument("-i", "--input", help="Reads the inputted CSV file to filter", action="store", required=True)
parser.add_argument("-o", "--output", help="Writes the filtered data onto a new CSV file under this name", action="store", required=True)
parser.add_argument("--unit", help="Specifies time units [seconds, s, or minutes, m]. Default is in seconds.", default="seconds", 
                    choices=["seconds", "s", "minutes", "m"], action="store")
parser.add_argument("--smooth", help="Smooths data points using N-point mean or median smoothing", choices=["mean", "median"], action="store")
parser.add_argument("-n", help="Specifies number of data points taken for smoothing", default=3, action="store", type=int)
args = parser.parse_args()

class DasSort:
    def __init__(self, file_input:pd.DataFrame, unit:str) -> None:
        self.indexes = None
        self.data = {
            "time": self.convert_time(file_input["time"], unit),
            "gps": self.gps_data(file_input["gps"]),
            "gps_lat": self.average_data(file_input["gps_lat"]),
            "gps_long": self.average_data(file_input["gps_long"]),
            "gps_alt": self.average_data(file_input["gps_long"]),
            "gps_course": self.average_data(file_input["gps_course"]),
            "gps_speed": self.average_data(file_input["gps_speed"]),
            "gps_satellites": self.average_data(file_input["gps_satellites"]),
            "ax": self.average_data(file_input["aX"]),
            "ay": self.average_data(file_input["aY"]),
            "az": self.average_data(file_input["aZ"]),
            "gx": self.average_data(file_input["gX"]),
            "gy": self.average_data(file_input["gY"]),
            "gz": self.average_data(file_input["gZ"]),
            "thermoc": self.average_data(file_input["thermoC"]),
            "thermof": self.average_data(file_input["thermoF"]),
            "pot": self.average_data(file_input["pot"]),
            "cadence": self.average_data(file_input["cadence"]),
            "power": self.average_data(file_input["power"]),
            "reed_velocity": self.average_data(file_input["reed_velocity"]),
            "reed_distance": self.average_data(file_input["reed_distance"])
        }

    def convert_time(self, milliseconds:pd.Series, unit) -> pd.Series:
        '''Returns the conversion of the time data points from milliseconds to the specified time unit, depending on the 
        argument passed by unit.
        
        unit accepts only seconds/s and minutes/m as arguments. 
        '''
        if unit == "seconds" or unit == "s":
            new_time = milliseconds / 1000
        elif unit == "minutes" or unit == "m":
            new_time = milliseconds / 1000 / 60
        else:
            raise ValueError("Argument only accepts either seconds/s or minutes/m")
        
        # sets the groups of indexes to use for averaging in future
        self.indexes = self.group_index(new_time)

        return range(1, len(self.indexes) + 1)

    def group_index(self, time:pd.Series) -> pd.Series:
        '''Returns a universal array of arrays of indexes, based on the specified time unit. Each array represents the indexes 
        of the data points within the same time interval. (eg. 1123ms and 1748ms are in the same time interval for seconds, 
        but 2453ms isn't)

        When given a valid value for args.unit, function will group the indexes within the same time interval in an array.
        Once all the indexes of a time interval has been accounted for, the array of indexes will be pushed into a
        universal array so that each element represents the data points of one singular time interval.
        '''
        universal_array = []
        index_array = []
        previous_time = 0

        for index in range(len(time)):
            if time[index] > previous_time:
                # if true, then time at time[i] is the next second/minute
                if previous_time != 0:
                    # appends index array into universal array, but ignores the first iteration
                    universal_array.append(index_array)

                previous_time = ceil(time[index])
                index_array = [] # recreates new array if previous time has changed
            index_array.append(index) 
        universal_array.append(index_array) # pushes the final array

        return universal_array

    def mean(self, data_array:pd.Series) -> float:
        '''Finds the average of a given set of numbers. 

        Disregards None and zero in calculation. Otherwise, if input is invalid, then raises error.
        '''
        total = 0
        length = len(data_array)
        for number in data_array:
            if number > 0 or number < 0:
                # 'number' value is valid
                total += number
            elif number == 0 or pd.isna(number):
                # None and zeroes are ignored
                length -= 1
                continue
            else:
                # 'number' value is invalid
                raise ValueError("Data point invalid and is neither zero nor None. The data point was "+str(number)+". ("+str(type(number))+")")
        try:
            return total/length
        except ZeroDivisionError:
            # in the event where length = 0, due to all the elements in data_array being ignored
            return 0 

    def average_data(self, data:pd.Series) -> pd.Series:
        '''Returns a column of new data points that has been averaged, based on specified time unit. 

        Finds the average of all data points within the same time interval. Appends this new value into an array, then continues
        to the next time interval. Once all time intervals have been accounted for, returns the set of new data points.
        '''
        average_data_array = []

        for index_array in self.indexes:
            current_average = self.mean(data[index_array])
            current_average = round(current_average, ndigits=2)
            average_data_array.append(current_average)

        return average_data_array
    
    def gps_data(self, data:pd.Series) -> pd.Series:
        '''Returns the data array of the time intervals which the GPS was turned on. 
        
        0 for when GPS was turned off, 1 for when turned on.
        '''
        new_gps_data = []

        for index_array in self.indexes:
            if 1 in data[index_array].values:
                new_gps_data.append(1)
            else:
                new_gps_data.append(0)

        return new_gps_data
    
    def smooth_caller(self, n:int, technique:str) -> None:
        '''Calls __mean_smooth function to smooth the data in instance variables, without requiring to refer to the variables themselves.'''
        if n < 3 or n > len(self.indexes):
            raise ValueError("Number of smoothing points must be at least 3 and less than the length of the data set to perform smoothing.")
        
        if technique == "mean":
            for variable in self.data:
                self.data[variable] = self.__mean_smooth(self.data[variable], n)
        elif technique == "median":
            for variable in self.data:
                self.data[variable] = self.__median_smooth(self.data[variable], n)

    def __mean_smooth(self, data:pd.Series, n:int) -> pd.Series:
        '''Returns an array of smoothed data based on number of data points taken to smooth. 
        
        For an odd number N, the data points are simply averaged. 
        Whereas for an even number N, the data points are averaged, then centered. This is because the data point will misalign with integer
        numbers of time if not done.'''
        smooth_data_array = [] 

        if n % 2 != 0: # Mean Smoothing for odd number N
            for i in range(len(data) - n + 1):
                data_points = data[i:i+n]
                new_data_point = self.mean(data_points)
                new_data_point = round(new_data_point, ndigits=2)
                smooth_data_array.append(new_data_point)
        else: # Mean Smoothing for even number N
            temp_array = []
            for i in range(len(data) - n + 1):
                data_points = data[i:i+N]
                new_data_point = self.mean(data_points)
                temp_array.append(new_data_point)
            
            # an extra step to centre the data by averaging adjacent data points
            for j in range(len(temp_array) - 1): 
                first = temp_array[j]
                second = temp_array[j+1]
                new_data_point = self.mean([first,second])
                new_data_point = round(new_data_point, ndigits=2)
                smooth_data_array.append(new_data_point)
        
        return smooth_data_array 
    
    def __median_smooth(self, data:pd.Series, n:int) -> pd.Series:
        '''Returns an array of smoothed data based on number of data points taken to smooth. 
        
        For an odd number N, the data points are simply averaged. 
        Whereas for an even number N, the data points are averaged, then centered. This is because the data point will misalign with integer
        numbers of time if not done.'''
        smooth_data_array = [] 

        if n % 2 != 0: # Median Smoothing for odd number N
            for i in range(len(data) - n + 1):
                data_points = data[i:i+n]
                new_data_point = median(data_points) # round not required, since it will always be the middle number
                smooth_data_array.append(new_data_point)
        else: # Median Smoothing for even number N
            temp_array = []
            for i in range(len(data) - n + 1):
                data_points = data[i:i+n]
                new_data_point = median(data_points)
                temp_array.append(new_data_point)
            
            # an extra step to centre the data by averaging adjacent data points
            for j in range(len(temp_array) - 1):
                first = temp_array[j]
                second = temp_array[j+1]
                new_data_point = median([first,second])
                new_data_point = round(new_data_point, ndigits=2)
                smooth_data_array.append(new_data_point)

        return smooth_data_array 
    
    def write_to_output_file(self, file_output:str) -> None:
        '''Creates new CSV file and writes new data onto CSV file.'''
        final_document = pd.DataFrame(self.data)
        final_document.to_csv(file_output, index=False)
        print(f"Success! Output is written to {file_output}")

if __name__ == '__main__':
    data = pd.read_csv(args.input) # Loads and reads CSV file
    das_sort = DasSort(data, args.unit) # Filters data in CSV file
    if args.smooth: # Applies smoothing technique, when provided
        das_sort.smooth_caller(args.n, args.smooth)
    das_sort.write_to_output_file(args.output) # Write filtered data into new CSV file
