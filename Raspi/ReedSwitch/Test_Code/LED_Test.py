import RPi.GPIO as GPIO
import time

pin = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin, GPIO.OUT)

GPIO.output(pin,GPIO.HIGH)
time.sleep(1)
GPIO.output(pin,GPIO.LOW)
