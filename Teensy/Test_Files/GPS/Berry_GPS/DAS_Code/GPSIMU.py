#-----------------------------------
# Name: Data Acquisition and MQTT to  Node RED
#
# Author: Angus Dunn
#
# Created: 28/10/2017
#
# A script that reads each line of the .nmea file as it is
# written by gpsmon and publishes it via mqtt.
# Copyright: None
#-----------------------------------
#!/usr/bin/env python3

import time
import sys
import socket
import paho.mqtt.client as mqtt
from datetime import date

def follow(thefile):
    # Follows the end of a file output like a tail

    thefile.seek(0,2)
    while True:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line

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
        print("Connected OK")
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

    mqtt.Client.connected_flag = False
    broker = get_ip_address()
    client = mqtt.Client()
    port = 1883

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message
    client.on_publish = on_publish
    client.on_message = on_message

    client.connect(broker, port)
    client.loop_start()

    # Subscribing to the buzzer callback
    client.subscribe("/Accelerometer/GPS/Buzzer")

    # Getting the .nmea file data
    title = "/home/pi/NMEADataFile.nmea"
    logfile = open(title,"r")
    loglines = follow(logfile)

    fixAcquired = False

    try:
        for line in loglines:
            line = line.split(',')

            if line[0] == '$GPGSA' and not fixAcquired:
                # Provides details on the nature of the GPS fix.
                # Example: $GPGSA,A,3,04,05,,09,12,,,24,,,,,2.5,1.3,2.1*39
                if int(line[2]) == 1:
                    client.publish("/Accelerometer/GPS/Fix",0)

                else:
                    client.publish("/Acceleration/GPS/Fix",1)
                    fixAcquired = True

            if line[0] == '$GPVTG' and fixAcquired:
                # Reading the vector track and speed over ground
                # Example: $GPVTG,054.7,T,034.4,M,005.5,N,010.2,K*48
                # print('Speed is ' + str(line[-3]) + 'km/h')
                client.publish("/Accelerometer/GPS/Speed", line[-3])

            if line[0] == '$GPRMC' and fixAcquired:
                # Reading the vector track and speed over ground, 1knot = 1.852km/h
                # Example: $GPRMC,123519,A,4807.038,N,01131.000,E,022.4,084.4,230394,003.1,W*6A
                # print('Speed is ' + str(round(float(line[7])*1.852,2)) + 'km/h')
                client.publish("/Accelerometer/GPS/Speed", round(float(line[7])*1.852,2))

            if line[0] == '$GPGGA' and fixAcquired:
                # Essential fix data which provide 3D location and accuracy data
                # Example: $GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47
                # print('Latitude is ' + str(line[2]) + line[3] + ', Longitude is ' + str(line[4]) + line[5])
                client.publish("/Accelerometer/GPS/Latitude", str(line[2]) + line[3])
                client.publish("/Accelerometer/GPS/Longitude", str(line[4]) + line[5])

            elif line[0] == '$GPGLL' and fixAcquired:
                # Gives the Latitude and Longitude of the GPS fix
                # Example: $GPGLL,4916.45,N,12311.12,W,225444,A,*1D
                # print('Latitude is ' + str(line[1]) + line[2] + ', Longitude is ' + str(line[3]) + line[4])
                client.publish("/Accelerometer/GPS/Latitude", str(line[1]) + line[2])
                client.publish("/Accelerometer/GPS/Longitude", str(line[3]) + line[4])

    except KeyboardInterrupt:
        client.loop_stop()
        client.disconnect()
