# ---------------------------------------------------------------------
# Last Modified:
#   30-12-2017
# Description:
#   This program is the test master. It decides which modules run append
#   and in what order.
# ---------------------------------------------------------------------

import subprocess
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

recording = 0
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)

print("")
try:
    while True:
        print("Ready!\n")
        while True:
            button_state = GPIO.input(24)
            if button_state == False:
                print("Starting Data Recording v2a...")
                recording = 1
                break
            sleep(0.2)

        p1 = subprocess.Popen(["python", "datav2a.py"])
        sleep(1)
        print("Recording!\n")

        while True:
            button_state = GPIO.input(24)
            if button_state == False:
                print("Stopping Data Recording v2a...")
                subprocess.Popen.kill(p1)
                recording = 0
                p3 = subprocess.call(
                    '/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Shell_Scripts/sendcsv.sh')
                print("Waiting.....\n\n")
                sleep(3)
                break
except KeyboardInterrupt:
    if recording == 1:
        print("\n\nStopping Data Recording v2a...\n")
        subprocess.Popen.kill(p1)
        print("Program Ended.\n")
    else:
        print("\n\nProgram Ended.\n")
    GPIO.cleanup()
