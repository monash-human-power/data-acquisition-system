class Sensors:

    # number of decimal places for the random generated val
    decimals = 2
    # percent range for the rangomly generated value
    percent_range = 0.05

    def CO2(val=325):
        # value in ppm (normal background conentration 250-400ppm)
        return round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)

    def humidity(val=75):
        # value as a percentage of humidity
        return round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)

    def temperature(val=20):
        # value in degrees celcius
        return round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)

    def accelerometer(val=5):
        # value in m/s^2 for all axis stored in a dictionary
        return {
        "x": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "y": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "z": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)}

    def gyroscope(val=90):
        # value in degrees for all axis stored in a dictionary
        return {
        "x": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "y": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "z": round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)}

    def battery(val=80):
        # value as a percentage of the battery
        return round(val + val*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)

    def reedSwitch(val=True):
        # value as either true or false
        return val

    def GPS(latLngVal=20, speedVal=50):
        # returns the latatude, longatude and the GPS speed of the bike stored in a dictionary
        return {
        "lat": round(latLngVal + latLngVal*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "lng": round(latLngVal + latLngVal*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals),
        "speed": round(speedVal + speedVal*random.uniform(-Sensors.percent_range, Sensors.percent_range), Sensors.decimals)}

    def steering(val=0):
        # value in degrees for the position of the steering stem
        return round(val + random.uniform(-90, 90), Sensors.decimals)

    def time():
        # return the current time for the sensor as Unix Epoch time
        return time.time()
