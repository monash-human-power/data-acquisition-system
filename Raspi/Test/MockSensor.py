

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
            if type(ave_val[0]) != int and type(ave_val[0]) != float:
                raise ValueError("""Single values must be either and int or a
                                 float""")
            self.single_val = True

        if len(ave_val) != 1:
            for sub_val in ave_val:
                if type(sub_val) != tuple:
                    raise ValueError("""Sub values must be stored as a tuple
                                    in the form (sub_value_name, ave_val)""")
class MockSensor:
        ave_val:        Either a single val that sets the average value for the

            self.single_val = False