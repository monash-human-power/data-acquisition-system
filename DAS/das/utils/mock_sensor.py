import random


class MockSensor:
    """Base class to make a mock sensor that produces random data"""

    def __init__(self, *average_value, percent_range=0.05, decimals=2, increment=False):
        """
        average_value:  Either a single value that sets the average value for
                        the sensor or a tuple of tuple subvalues formatted as
                        (sub_value_name, average_value). Where
                        sub_value_name is the name that will be used in the
                        outputted dictionary and the average_value is similar
                        to a single value.
        percent_range:  Percent range for the randomly generated value
        decimals:       Number of decimal places for the random generated val
        increment:      Whether to increase the value or generate a new value.
                        If increasing value, will increase it by percent_range.
                        Currently only implemented for the single value
                        MockSensor, if there are multiple values, this option
                        will be ignored.
        """

        self.average_value = average_value
        self.percent_range = percent_range
        self.decimals = decimals
        self.increment = increment

        if len(average_value) == 1:
            if not isinstance(average_value[0], int) and not isinstance(
                average_value[0], float
            ):
                raise TypeError("""Single values must be either and int or a float""")
            self.single_val = True

        else:
            for sub_value in average_value:
                if not isinstance(sub_value, tuple):
                    raise TypeError(
                        """Sub values must be stored as a tuple in the form (sub_valueue_name, average_value)"""
                    )
            self.single_val = False

    def get_value(self):
        """Generates the random data as a float for a single val and a dict for multiple sub values"""

        if self.single_val:
            return self.gen_single_value(self.average_value[0])

        else:
            sensor_dict = {}
            for sub_value in self.average_value:
                sub_value_name = sub_value[0]
                sub_average_value = sub_value[1]
                if isinstance(sub_average_value, int) or isinstance(
                    sub_average_value, float
                ):
                    sensor_dict[sub_value_name] = self.gen_single_value(
                        sub_average_value
                    )
                else:
                    sensor_dict[sub_value_name] = sub_average_value

            return sensor_dict

    def gen_single_value(self, average_value):
        """Generates a single value given an average value"""
        sensor_val = average_value
        sensor_val += average_value * random.uniform(
            -self.percent_range, self.percent_range
        )
        sensor_val = round(sensor_val, self.decimals)
        if self.increment and self.single_val:
            new_value = average_value + abs(average_value - sensor_val)
            self.average_value = (new_value,)
            return new_value
        return sensor_val
