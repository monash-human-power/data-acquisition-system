import RPi.GPIO as GPIO
import time
import subprocess

button_pin = 27
led_pin = 17

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(led_pin, GPIO.OUT)

button_previous = 1
record = 0

# Initialization routine
GPIO.output(led_pin, True)
time.sleep(0.2)
GPIO.output(led_pin, False)
time.sleep(0.2)
GPIO.output(led_pin, True)
time.sleep(0.2)
GPIO.output(led_pin, False)
time.sleep(0.2)
GPIO.output(led_pin, True)
time.sleep(0.2)
GPIO.output(led_pin, False)

while True:
    button_next = GPIO.input(button_pin)

    if (button_next != button_previous and button_next == 0):
        if (record == 0):
            GPIO.output(led_pin, True)
            p1 = subprocess.Popen(["python", "/home/pi/Documents/MHP_DAS/Raspi/ReedSwitch/rs_simple.py"])
            record = 1
        else:
            GPIO.output(led_pin, False)
            subprocess.Popen.kill(p1)
            subprocess.call(["bash", "/home/pi/Documents/MHP_DAS/Raspi/ReedSwitch/transfer.sh"])
            record = 0

    button_previous = button_next
