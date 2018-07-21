import csv
import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

filename = "/home/pi/Documents/MHP_raspicam/Hall_Effect/switch_data.csv"
file = open(filename, 'w')
filewrite = csv.writer(file, delimiter=',', lineterminator='\n')

init_time = time.time()

try:
    while True:
        button_state = GPIO.input(24)
        if button_state == False:
            print "Switch closed."
            time_elapsed = round(time.time() - init_time, 5)
            filewrite.writerow([time_elapsed, 1])
        else:
            print "Switch open."
            time_elapsed = round(time.time() - init_time, 5)
            filewrite.writerow([time_elapsed, 0])
        time.sleep(0.01)
except KeyboardInterrupt:
    GPIO.cleanup()
