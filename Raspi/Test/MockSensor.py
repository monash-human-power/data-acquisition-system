import random


class MockSensor:
    """ Base class to make a mock sensor that produces random data"""

    def __init__(self, *ave_val, percent_range=0.05, decimals=2):
        """
        ave_val:        Either a single val that sets the average value for the
                        sensor or and array of subvals formatted as
                        (sub_value_name, ave_val). Where sub_value_name is the
                        name that will be used in the outputed dictionary and
                        the ave_val is similar to a single val.
        percent_range:  Percent range for the randomly generated value
        decimals:       Number of decimal places for the random generated val
        """

        self.ave_val = ave_val
        self.percent_range = percent_range
        self.decimals = decimals

        if len(ave_val) == 1:
            if (not isinstance(ave_val[0], int)
               and not isinstance(ave_val[0], float)):
                raise ValueError("""Single values must be either and int or a
                                 float""")
            self.single_val = True

        else:
            for sub_val in ave_val:
                if not isinstance(sub_val, tuple):
                    raise ValueError("""Sub values must be stored as a tuple
                                    in the form (sub_value_name, ave_val)""")
            self.single_val = False

    def get_value(self):
        """ Generates the random data as a float for a single val and a dict
            for mutliple sub values"""

        if self.single_val:
            return self.gen_single_value(self.ave_val[0])

        else:
            sensor_dict = {}
            for sub_val in self.ave_val:
                sub_val_name = sub_val[0]
                sub_ave_val = sub_val[1]
                sensor_dict[sub_val_name] = self.gen_single_value(sub_ave_val)

            return sensor_dict

    def gen_single_value(self, ave_val):
        """ Generates a single value given an average value"""
        sensor_val = ave_val
        sensor_val += ave_val * random.uniform(-self.percent_range,
                                               self.percent_range)
        sensor_val = round(sensor_val, self.decimals)
        return sensor_val
