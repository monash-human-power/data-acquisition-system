import serial
import time
#from paho.mqtt import client

ser = serial.Serial('COM3', 9600)
print("Arduino connected...")
time.sleep(1)
# MQTT Setup


client_id = "Ammanuel" # 
broker_id = 3 # change
topic_string = "trike/lap/trigger"
start_message ="start timer"
lap_message = "lap"


mqtt = client.Client(client_id)

connected = False
while not connected:
        print("Connecting to MQTT...")
        try:
            mqtt.connect(broker_id)
            print("MQTT connected...")
            connected = True
        except:
            print("Failed to connect. Retrying...")
            time.sleep(1)



while True:
    message = ser.readline().decode().strip()
    if message:
        print(message) 
    
        if message == start_message: 
            mqtt.publish(topic_string, message)
        elif message == lap_message:
            mqtt.publish(topic_string, message)
        

