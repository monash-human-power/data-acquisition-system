import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("connected OK Returned code=",rc)
        
    else:
        print("Bad connection Returned code=",rc)

def on_message(client, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass


client = mqtt.Client("python1")

client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect
client.username_pw_set("punbssjf", "N5R0WZ4gQD9y")
client.connect("soldier.cloudmqtt.com", 11989)

start_topic = "/v3/wireless-module/3/start"
stop_topic = "/v3/wireless-module/3/stop"

print("publishing msg at : " + start_topic)
client.publish(start_topic, "start")
time.sleep(10)
client.publish(stop_topic, "stop")

# Continue the network loop, exit when an error occurs
client.loop_forever()












