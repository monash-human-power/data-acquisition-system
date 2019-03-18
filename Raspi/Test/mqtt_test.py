import sys
import time
import paho.mqtt.client as mqtt

# TODO: Take in time and length of time
def start_publishing(client):
    start_time = round(time.time(),2)
    while(True):
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)
        data = "gps=1&gps_location=00&gps_course=00&gps_speed=00&gps_satellites=00"
        data += "&aX=00.0000&aY=00.0000&aZ=00.0000&gX=00.0000&"
        data += "gY=00.0000&gZ=00.0000"
        data += "&thermoC=25.00&thermoF=25.00"
        data += "&pot=100"
        data += "&filename=test.csv"
        data += "&time=" + str(total_time * 1000)
        data += "&power=100&cadence=100"
        client.publish("data", data)
        print(data)
        time.sleep(0.5)
        if (total_time > 5):
            break
    print("End program")
    sys.exit(0)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))

broker_address = "localhost"
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address)
start_publishing(client)

client.loop_forever()