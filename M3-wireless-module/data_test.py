import paho.mqtt.client as mqtt
import time

data_topic = "/v3/wireless-module/3/data"

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
        client.subscribe("/v3/wireless-module/#")
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, obj, msg):
    print(msg.topic + " : " + str(msg.payload))

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass


client = mqtt.Client("python2")

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect
client.username_pw_set("punbssjf", "N5R0WZ4gQD9y")
client.connect("soldier.cloudmqtt.com", 11989)

# Continue the network loop, exit when an error occurs
client.loop_forever()