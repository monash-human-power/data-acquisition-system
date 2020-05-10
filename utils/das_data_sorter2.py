import pandas as pd 
from argparse import ArgumentParser
from numpy import median, mean, ceil
from typing import TypeVar

D = TypeVar('DAS_data') # data type to represent columns of the data in a given file

# accepts terminal arguments
parser = ArgumentParser()
args = parser.parse_args()
parser.add_argument("--file", help="Input CSV file", action="store", required=True)
parser.add_argument("--output", help="Returns the filtered data", default="filtered_data.csv", action="store")
parser.add_argument("--unit", help="Specify time units (seconds, s, or minutes, m)", default="seconds", 
                    choices=["seconds", "s", "minutes", "m"], action="store")

class DasSort:
    def __init__(self, data:str) -> None:
        self.indexes = None
        self.time = self.__convert_time__(data["time"])
        self.gps = self.__average_data__(data["gps"])
        self.gps_location = self.__average_data__(data["gps_location"])
        self.gps_course = self.__average_data__(data["gps_course"])
        self.gps_speed = self.__average_data__(data["gps_speed"])
        self.gps_satelite = self.__average_data__(data["gps_satellite"])
        self.ax = self.__average_data__(data["aX"])
        self.ay = self.__average_data__(data["aY"])
        self.az = self.__average_data__(data["aZ"])
        self.gx = self.__average_data__(data["gX"])
        self.gy = self.__average_data__(data["gY"])
        self.gz = self.__average_data__(data["gz"])
        self.thermoc = self.__average_data__(data["thermoC"])
        self.thermof = self.__average_data__(data["thermoF"])
        self.pot = self.__average_data__(data["pot"])
        self.cadence = self.__average_data__(data["cadence"])
        self.power = self.__average_data__(data["power"])
        self.reed_velocity = self.__average_data__(data["reed_velocity"])
        self.reed_distance = self.__average_data__(data["reed_distance"])

    def __convert_time__(self, milliseconds:D) -> D:
        '''Returns the conversion of the time data points from milliseconds to the specified time unit, depending on the 
        argument passed by args.unit.
        
        args.unit accepts only seconds/s and minutes/m as arguments. 
        '''
        if args.unit == "seconds" or args.unit == "s":
            milliseconds = milliseconds/1000
        elif args.unit == "minutes" or args.unit == "m":
            milliseconds = milliseconds/1000/60
        else:
            raise ValueError("Argument only accepts either seconds/s or minutes/m")
        
        # sets the groups of indexes to use for averaging in future
        self.indexes = self.__index_groups__(milliseconds)

        return range(1,len(self.indexes)+1)

    def __index_groups__(self, time:D) -> D:
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
    
    def __average_data__(self, data:D) -> D:
        '''Returns a column of new data points that has been averaged, based on specified time unit. 

        Finds the average of all data points within the same time interval. Appends this new value into an array, then continues
        to the next time interval. Once all time intervals have been accounted for, returns the set of new data points.
        '''
        avg_data = []

        for index_array in self.indexes:
            avg = mean(self.indexes[index_array])
            avg = round(avg, ndigits=2)
            avg_data.append(avg)

        return avg_data
    
    def __print_output_file__(self) -> None:
        '''Creates new CSV file and writes new data onto CSV file.'''
        final = pd.DataFrame({
            "time": self.time,
            "gps": self.gps,
            "gps_location": self.gps_location,
            "gps_course": self.gps_course,
            "gps_speed": self.gps_speed,
            "gps_satellite": self.gps_satellite,
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
        final.to_csv(args.output, index=False)
        print("Finish! Check in the same folder for the new CSV file.")

if __name__ == '__main__':
    data = pd.read_csv(args.file)
    das_sort = DasSort(data)
