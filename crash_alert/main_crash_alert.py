import paho_mqtt.src.paho.mqtt.client as mqtt #import the client1
from crash_alert import CrashAlert
import time
from distutils.util import strtobool
############
crash_alert = CrashAlert(5)

def on_message(client, userdata, message):
    string_received = str(message.payload.decode("utf-8"))
    boolean = strtobool(string_received)
    if boolean:
        print(crash_alert.alert())
    print("message received", string_received)
    print("message time=",time.strftime("%H:%M:%S"))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

########################################
broker_address="localhost"
#broker_address=local
print("creating new instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker")
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic","crash_alert")
client.subscribe("crash_alert")
msg = input("Enter message: ")
while msg != "stop":
    print("Publishing message to topic","crash_alert")
    client.publish("crash_alert", msg)
    time.sleep(0.5)
    msg = input("Enter message: ")
client.loop_stop() #stop the loop