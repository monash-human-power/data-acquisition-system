import sys
import time
import random
import argparse
import paho.mqtt.client as mqtt

# Arguments
parser = argparse.ArgumentParser(description='DAS MQTT python script', add_help=True)
parser.add_argument('-t', '--time', action='store', type=int, default=1, help="length of time to send data")
parser.add_argument('-r', '--rate', action='store', type=float, default=0.5, help="rate of data in seconds")
parser.add_argument('--host', action='store', type=str, default="localhost", help="address of the MQTT broker")

args = parser.parse_args()
def start_publishing(client):
    start_time = round(time.time(),2)
    print("start")
    client.publish("start")
    gps_speed = 0
    while(True):
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)

        # Generate data message
        data = "gps=1&gps_location=00&gps_course=00&"
        gps_speed = random.random() * (total_time) + gps_speed
        data += "gps_speed=" + str(gps_speed)
        data += "&gps_satellites=00"
        data += "&aX=00.0000&aY=00.0000&aZ=00.0000&gX=00.0000&"
        data += "gY=00.0000&gZ=00.0000"
        data += "&thermoC=25.00&thermoF=25.00"
        data += "&pot=100"
        data += "&filename=test.csv"
        data += "&time=" + str(total_time * 1000)
        data += "&power=" + str(random.randint(0,150))
        data += "&cadence=" + str(random.randint(0,150))
        client.publish("data", data)
        print(data)

        time.sleep(args.rate)
        if (total_time >= args.time):
            break
    print("stop")
    client.publish("stop")
    sys.exit(0)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))

broker_address = args.host
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address)
start_publishing(client)

client.loop_forever()