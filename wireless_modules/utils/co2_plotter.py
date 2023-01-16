# A quick and dirty script to plot the published CO2 data from the WM.

import paho.mqtt.client as mqtt
import time
import json
import matplotlib.pyplot as plt

times = []
values = []

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim([0, 1000])
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Measured CO2 (ppm)")
(line1,) = ax.plot(times, values)

start_time = time.time()


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    #     print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    data = json.loads(msg.payload.decode("utf-8"))
    for sensor in data["sensors"]:
        if sensor["type"] == "co2":
            times.append(time.time() - start_time)
            values.append(sensor["value"])

            line1.set_xdata(times)
            line1.set_ydata(values)
            fig.canvas.draw()
            fig.canvas.flush_events()
            ax.set_xlim([times[0], times[-1]])


def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# If you want to use a specific client id, use
# mqttc = mqtt.Client("client-id")
# but note that the client id must be unique on the broker. Leaving the client
# id parameter empty will generate a random id for you.
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
# Uncomment to enable debug messages
# mqttc.on_log = on_log
mqttc.connect("localhost", 1883, 60)
mqttc.subscribe("/v3/wireless_module/3/data", 0)

mqttc.loop_forever()
