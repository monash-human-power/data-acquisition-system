import RPi.GPIO as GPIO
import time

pin = 27

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

while True:
    input_state = GPIO.input(pin)
    if input_state == False:
        print("Button Pressed")
        time.sleep(0.2)

