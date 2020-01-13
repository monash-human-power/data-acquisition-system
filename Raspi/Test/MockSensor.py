import random


class MockSensor:
    """ Base class to make a mock sensor that produces random data"""

    def __init__(self, *average_value, percent_range=0.05, decimals=2):
        """
        average_value:  Either a single val that sets the average value for the
                        sensor or an array of subvals formatted as
                        (sub_value_name, average_value). Where sub_value_name
                        is the name that will be used in the outputted
                        dictionary and the average_value is similar to a single
                        val.
        percent_range:  Percent range for the randomly generated value
        decimals:       Number of decimal places for the random generated val
        """

        self.average_value = average_value
        self.percent_range = percent_range
        self.decimals = decimals

        if len(average_value) == 1:
            if (not isinstance(average_value[0], int)
               and not isinstance(average_value[0], float)):
                raise TypeError("""Single values must be either and int or a
                                 float""")
            self.single_val = True

        else:
            for sub_val in average_value:
                if not isinstance(sub_val, tuple):
                    raise TypeError("""Sub values must be stored as a tuple
                                    in the form (sub_value_name, average_value)
                                    """)
            self.single_val = False

    def get_value(self):
        """ Generates the random data as a float for a single val and a dict
            for mutliple sub values"""

        if self.single_val:
            return self.gen_single_value(self.average_value[0])

        else:
            sensor_dict = {}
            for sub_val in self.average_value:
                sub_val_name = sub_val[0]
                sub_average_value = sub_val[1]
                sensor_dict[sub_val_name] = self.gen_single_value(sub_average_value)

            return sensor_dict

    def gen_single_value(self, average_value):
        """ Generates a single value given an average value"""
        sensor_val = average_value
        sensor_val += average_value * random.uniform(-self.percent_range,
                                                     self.percent_range)
        sensor_val = round(sensor_val, self.decimals)
        return sensor_val
