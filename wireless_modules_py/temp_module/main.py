import time
import os
os.environ['PI_HOST']='127.0.0.1'
os.environ['PI_PORT']='8888'
import sys
import Adafruit_DHT
DHT_SENSOR=Adafruit_DHT.DHT22
DHT_PIN=....
while True:
    try: 
        humidity, temperature=Adafruit_DHT.read_retry(DHT_SENSOR,DHT_PIN)
        if humidity is not None and temperature is not None:
            print("Temperature={0:0.1f}C Humidity={1:0.1f}%".format(temperature,humidity))
        else:
            print ("failed to obtain data")
    except KeyboardInterrupt:
        break
    time.sleep(2.0)
