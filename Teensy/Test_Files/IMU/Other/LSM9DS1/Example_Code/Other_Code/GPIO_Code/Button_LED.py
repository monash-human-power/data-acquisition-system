import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

GPIO.setup(18,GPIO.OUT)
GPIO.setup(24,GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
	while True:
		button_state = GPIO.input(24)
		if button_state == False:
			print "Button Pressed, LED on"
			GPIO.output(18,GPIO.HIGH)
			time.sleep(0.2)
		else:
			print "Button not pressed, LED off"
			GPIO.output(18,GPIO.LOW)
			time.sleep(0.2)
except:
	GPIO.cleanup()

