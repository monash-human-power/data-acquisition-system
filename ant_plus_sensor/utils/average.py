import functools
import time as time_mod

"""
Calculate a rolling average on a set of data points
"""
class RollingAverage:
    def __init__(self, interval):
        """

        Create a rolling average counter
        
        @param interval (float): Length of rolling interval window in milliseconds

        """
        self.interval = interval
        self.points = []

    def add(self, value):
        """

        Add data point to average
        
        @param value (number): Value
        
        """
        time = time_mod.time() * 1000
        self.points.append([time, value])
    
    def average(self):
        """

        Remove all stale values

        @return average (float): Average

        """
        time = time_mod.time() * 1000;
        self.points = filter(lambda x: x[0] >= time - self.interval, self.points)
        sum = functools.reduce(lambda acc, curr: acc + curr[1], self.points, 0)
        average = sum / len(self.points)
        return average
