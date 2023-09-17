import serial
import time
#from paho.mqtt import client

ser = serial.Serial('COM3', 9600)
# MQTT Setup
"""

client_id = "Ammanuel" # 
broker_id = 3 # change
topic_string_1 = "/start"
topic_string_2 = "/lap"
start_message ="start"
lap_message = "lap"


mqtt = client.Client(client_id)

connected = False
while not connected:
        print("Connectiing...")
        try:
            mqtt.connect(broker_id)
            connected = True
        except:
            print("Failed to connect. Retrying...")
            time.sleep(1)

"""

while True:
    message = ser.readline().decode().strip()
    if message:
        print(message) 
        """
        if message == start_message: 
            mqtt.publish(topic_string_1, message)
        elif message == lap_message:
            mqtt.publish(topic_string_2, message)
        """

