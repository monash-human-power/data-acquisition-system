#-----------------------------------
# Name: Hall Effect Sensor
#
# Author: Angus Dunn
#
# Created: 28/10/2017
#
# A script that reads the value of the hall effect sensor
# and converts it to distance travelled and speed
# Copyright: None
#-----------------------------------
#!/usr/bin/env python3

import time
import math
import socket
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import datetime

def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def on_log(client, serdata, level, buf):
    print(buf)

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        #print("Connected OK")
    else:
        print("Bad connection, returned code: ",rc)
        client.loop_stop()

def on_disconnect(client, userdata, rc):
    print("Client disconnected OK")

def on_publish(client, userdata, mid):
    print("In on_pub callback mid = ",mid)

def on_message(client,userdata, message):
    topic = message.topic
    msgr = str(message.payload.decode("utf-8)"))
    msgr = "Message Received "+msgr

if __name__ == '__main__':

    # Pin Definitions
    hallEffect = 4

    # Setup GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(hallEffect,GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Setting MQTT parameters
    mqtt.Client.connected_flag = False
    broker = get_ip_address()
    client = mqtt.Client()
    port = 1883

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    client.on_publish = on_publish

    # Connect to MQTT broker
    client.connect(broker, port)
    client.loop_start()

    # Initialise RPM and distance
    thenTime = datetime.datetime.now()
    pi = math.pi
    wheel_radius = 5 # in meters
    circumference = 2 * pi * wheel_radius
    distance = 0

    # Infinite Loop
    try:
        while True:
            GPIO.wait_for_edge(hallEffect, GPIO.FALLING)

            # Calculating speed
            nowTime = datetime.datetime.now()
            time_difference = nowTime - thenTime
            thenTime = nowTime
            elapsed_time = time_difference.seconds + time_difference.microseconds/10**6
            Speed = circumference / elapsed_time
            client.publish("/Accelerometer/HallEffect/Speed", round(Speed,2))

            # Calculating distance
            distance += circumference
            client.publish("/Accelerometer/HallEffect/Distance", round(distance,2))

    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
        GPIO.cleanup()

