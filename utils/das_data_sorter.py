import pandas as pd 
from argparse import ArgumentParser
from numpy import ceil

# accepts terminal arguments
parser = ArgumentParser()
parser.add_argument("--input", help="Reads the inputted CSV file to filter", action="store", required=True)
parser.add_argument("--output", help="Writes the filtered data onto a new CSV file under this name", action="store", required=True)
parser.add_argument("--unit", help="Specify time units [seconds, s, or minutes, m]. Default is in seconds.", default="seconds", 
                    choices=["seconds", "s", "minutes", "m"], action="store")
args = parser.parse_args()

class DasSort:
    def __init__(self, file_input:pd.DataFrame, file_output:str, unit:str) -> None:
        self.indexes = None
        self.time = self.convert_time(file_input["time"], unit)
        self.gps = self.average_data(file_input["gps"])
        self.gps_location = self.location_data(file_input["gps_location"])
        self.gps_course = self.average_data(file_input["gps_course"])
        self.gps_speed = self.average_data(file_input["gps_speed"])
        self.gps_satellites = self.average_data(file_input["gps_satellites"])
        self.ax = self.average_data(file_input["aX"])
        self.ay = self.average_data(file_input["aY"])
        self.az = self.average_data(file_input["aZ"])
        self.gx = self.average_data(file_input["gX"])
        self.gy = self.average_data(file_input["gY"])
        self.gz = self.average_data(file_input["gZ"])
        self.thermoc = self.average_data(file_input["thermoC"])
        self.thermof = self.average_data(file_input["thermoF"])
        self.pot = self.average_data(file_input["pot"])
        self.cadence = self.average_data(file_input["cadence"])
        self.power = self.average_data(file_input["power"])
        self.reed_velocity = self.average_data(file_input["reed_velocity"])
        self.reed_distance = self.average_data(file_input["reed_distance"])

        self.write_to_output_file(file_output)

    def convert_time(self, milliseconds:pd.Series, unit) -> pd.Series:
        '''Returns the conversion of the time data points from milliseconds to the specified time unit, depending on the 
        argument passed by unit.
        
        unit accepts only seconds/s and minutes/m as arguments. 
        '''
        if unit == "seconds" or unit == "s":
            new_time = milliseconds/1000
        elif unit == "minutes" or unit == "m":
            new_time = milliseconds/1000/60
        else:
            raise ValueError("Argument only accepts either seconds/s or minutes/m")
        
        # sets the groups of indexes to use for averaging in future
        self.indexes = self.group_index(new_time)

        return range(1,len(self.indexes)+1)

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

        for i in range(len(time)):
            if time[i] > previous_time:
                # if true, then time at time[i] is the next second/minute
                if previous_time != 0:
                    # appends index array into universal array, but ignores the first iteration
                    universal_array.append(index_array)

                previous_time = ceil(time[i])
                index_array = [] # recreates new array if previous time has changed
            index_array.append(i) 

        # pushes the final array when for loop has completed
        universal_array.append(index_array)

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
    
    # def gps_data(self, data:pd.Series) -> pd.Series:
        '''currently doesn't work as intended'''
        
    #     new_gps_data = []
    #     for index_array in self.indexes:
    #         if 1 is in data[index_array]:
    #             new_gps_data.append(1)
    #         else:
    #             new_gps_data.append(0)
        
    #     return new_gps_data

    def location_data(self, data:pd.Series) -> pd.Series:
        '''Handles the certain gps data and returns the data point at the last element of each time interval. 

        gps_location requires a separate function because the values are strings, whereas the other data columns are 
        integers/floats. Handles it so that it will always return the location data at the last element of each time interval.
        '''
        new_location_data = []
        for index_array in self.indexes:
            last_element_index = index_array[-1] 
            last_element = data[last_element_index]
            new_location_data.append(last_element)
        
        return new_location_data
    
    def write_to_output_file(self, file_output:str) -> None:
        '''Creates new CSV file and writes new data onto CSV file.'''
        final = pd.DataFrame({
            "time": self.time,
            "gps": self.gps,
            "gps_location": self.gps_location,
            "gps_course": self.gps_course,
            "gps_speed": self.gps_speed,
            "gps_satellites": self.gps_satellites,
            "aX": self.ax,
            "aY": self.ay,
            "aZ": self.az,
            "gX": self.gx,
            "gY": self.gy,
            "gZ": self.gz,
            "thermoC": self.thermoc,
            "tempF": self.thermof,
            "pot": self.pot,
            "cadence": self.cadence,
            "power": self.power,
            "reed_velocity": self.reed_velocity,
            "reed_distance": self.reed_distance
        })
        final.to_csv(file_output, index=False)
        print(f"Success! Output is written to {file_output}")

if __name__ == '__main__':
    data = pd.read_csv(args.input)
    das_sort = DasSort(data, args.output, args.unit)
