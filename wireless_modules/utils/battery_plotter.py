"""
A quick and dirty script to plot/log the published battery data from the WM.
"""

import paho.mqtt.client as mqtt
import time
import json
import matplotlib.pyplot as plt

times = []
values = []

plt.ion()

fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_ylim([2.8, 4.3])
ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Battery voltage")
(line1,) = ax.plot(times, values)

out_file = open("battery_output.csv", "a")
out_file.write("time,voltage\n")

start_time = time.time()


def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

    data = json.loads(msg.payload.decode("utf-8"))

    message_time = time.time() - start_time
    message_data = data["voltage"]

    out_file.write(f"{message_time},{message_data}\n")
    out_file.flush()

    times.append(message_time)
    values.append(message_data)

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
mqttc.subscribe("/v3/wireless_module/3/battery", 0)

mqttc.loop_forever()
