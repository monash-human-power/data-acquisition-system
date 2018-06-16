# MODEL B SIDE

from time import sleep
import subprocess
import socket
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)

print("\nReady to initialise!\n")
GPIO.output(17, GPIO.HIGH)
GPIO.output(27, GPIO.LOW)

online = 0
MESSAGE = "STOP"

PiZero1MAC = 'b8:27:eb:3b:26:bb'
PiZero2MAC = 'b8:27:eb:19:78:4c'
PiZero3MAC = 'b8:27:eb:f:69:e5'
PiZero4MAC = 'b8:27:eb:5f:91:1a'
PiZero5MAC = 'b8:27:eb:3c:c9:14'
PiZero6MAC = 'b8:27:eb:21:f0:52'
MAC_List = [PiZero1MAC, PiZero2MAC, PiZero3MAC, PiZero4MAC, PiZero5MAC, PiZero6MAC]

while online < 2:
    online = 0
    GPIO.output(17, GPIO.HIGH)
    GPIO.output(27, GPIO.HIGH)
    button_state = GPIO.input(24)
    if button_state == False:
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        sleep(0.2)
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.HIGH)
        sleep(0.2)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        sleep(0.2)
        GPIO.output(17, GPIO.HIGH)
        GPIO.output(27, GPIO.HIGH)
        sleep(0.2)
        GPIO.output(17, GPIO.LOW)
        GPIO.output(27, GPIO.LOW)
        hold = 0

        print("Configuring Pi Networking\n")

        index = 0
        Online_List = [0] * len(MAC_List)
        path = '/home/pi/Documents/MHP_raspicam/Accelerometers/LSM9DS1/BumpTest_Code/Shell_Scripts/piscan.sh'
        for MAC in MAC_List:
            IP = subprocess.check_output([path, MAC])
            Online_List[index] = IP
            if IP != '0':
                print("Found Pi @ %s\n" % IP)
                GPIO.output(27, GPIO.HIGH)
                sleep(0.2)
                GPIO.output(27, GPIO.LOW)
                online = online + 1
            index = index + 1
        if online == 2:
            print("Successful configuration!\n")
        else:
            print("Try again....\n")

print("Ready for button press!\n")
GPIO.output(17, GPIO.HIGH)
GPIO.output(27, GPIO.LOW)

try:
    while True:
        button_state = GPIO.input(24)
        if button_state == False:
            if MESSAGE == "STOP":
                print("Starting Data Recording!\n")
                MESSAGE = "START"
                GPIO.output(17, GPIO.LOW)
                GPIO.output(27, GPIO.HIGH)
            else:
                print("Stopping Data Recording!\n")
                MESSAGE = "STOP"
                GPIO.output(17, GPIO.HIGH)
                GPIO.output(27, GPIO.LOW)

            for IP in Online_List:
                if IP == '0':
                    continue

                UDP_IP = IP
                UDP_PORT = 5005

                sock = socket.socket(socket.AF_INET,  # Internet
                                     socket.SOCK_DGRAM)  # UDP
                sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

            print("Ready for button press!\n")
        sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()
    if MESSAGE == "START":
        print("\n\nStopping Data Recording!\n")
        for IP in Online_List:
            if IP == '0':
                continue

            UDP_IP = IP
            UDP_PORT = 5005

            MESSAGE = "STOP"

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
        print("Program Ended.\n")
    else:
        print("\n\nProgram Ended.\n")
