import time
import argparse
import json
import paho.mqtt.client as mqtt
from MockSensor import MockSensor

parser = argparse.ArgumentParser(
    description='MQTT wireless module test script that sends fake data',
    add_help=True)
parser.add_argument(
    '-t', '--time', action='store', type=int,
    default=float('Inf'), help="""Length of time to send data in seconds
    (duration). If nothing is selected it will continuously send out data.""")
parser.add_argument(
    '-r', '--rate', action='store', type=float, default=5,
    help="""Rate of data in data sent per second. Default is 5 data pack sent
    per second.""")
parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")
parser.add_argument(
    '-i', '--id', action='store', type=int, default=None,
    help="""Specify the module to produce fake data. eg. --id 1 specifies that
    module 1 only produces data. If nothing is given all modules will be
    active.""")

# Generate the fake sensors with average values
s_steering_angle = MockSensor(10)
s_co2 = MockSensor(325)
s_temperature = MockSensor(25)
s_humidity = MockSensor(85)
s_reed_velocity = MockSensor(50)
s_battery = MockSensor(80)
s_accelerometer = MockSensor(("x", 90),
                             ("y", 90),
                             ("z", 90))
s_gyroscope = MockSensor(("x", 90),
                         ("y", 90),
                         ("z", 90))
s_gps = MockSensor(("speed", 50),
                   ("satellites", 10),
                   ("latitude", 25),
                   ("longitude", 25),
                   ("altitude", 50),
                   ("course", 0))


def send_fake_data(client, duration, rate, module_id):
    """ Send artificial data over MQTT for each module chanel. Sends [rate] per
    second for [duration] seconds"""

    start_time = round(time.time(), 2)
    total_time = 0
    battery_duration = 5 * 60   # Battery info to be published every 5min
    battery_counter = 0         # Battery counter to determine when to publish

    while total_time < duration:
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)
        publish_battery = (battery_counter * battery_duration) <= total_time

        # TODO: create function that outputs the wireless data output so that
        # it can be compaired with the the data read by the wireless logging
        # script

        def publish_data_and_battery(module_num):
            battery_data = {
                "module-id": module_num,
                "percentage": s_battery.get_value()
            }

            module_topic = "/v3/wireless-module/"+str(module_num)+"/data"
            battery_topic = "/v3/wireless-module/"+str(module_num)+"/battery"

            publish(client, module_topic, module_data)
            if publish_battery:
                publish(client, battery_topic, battery_data)

        if publish_battery:
            battery_counter += 1

        # Wireless module 1 (Middle)
        if module_id == 1 or module_id is None:
            module_num = 1
            module_data = {
                            "sensors": [
                                {
                                    "type": "temperature",
                                    "value": s_temperature.get_value()
                                },
                                {
                                    "type": "humidity",
                                    "value": s_humidity.get_value()
                                },
                                {
                                    "type": "steeringAngle",
                                    "value": s_steering_angle.get_value()
                                }
                             ]
                          }
            publish_data_and_battery(module_num)

        # Wireless module 2 (Back)
        if module_id == 2 or module_id is None:
            module_num = 2
            module_data = {
                            "sensors": [
                                {
                                    "type": "co2",
                                    "value": s_co2.get_value()
                                },
                                {
                                    "type": "temperature",
                                    "value": s_temperature.get_value()
                                },
                                {
                                    "type": "humidity",
                                    "value": s_humidity.get_value()
                                },
                                {
                                    "type": "accelerometer",
                                    "value": s_accelerometer.get_value()
                                },
                                {
                                    "type": "gyroscope",
                                    "value": s_gyroscope.get_value()
                                }
                             ]
                          }
            publish_data_and_battery(module_num)

        # Wireless module 3 (Front)
        if module_id == 3 or module_id is None:
            module_num = 3
            module_data = {
                            "sensors": [
                                {
                                    "type": "co2",
                                    "value": s_co2.get_value()
                                },
                                {
                                    "type": "reedVelocity",
                                    "value": s_reed_velocity.get_value()
                                },
                                {
                                    "type": "gps",
                                    "value": s_gps.get_value()
                                }
                             ]
                          }
            publish_data_and_battery(module_num)

        print()  # Newline for clarity
        time.sleep(1/rate)


def publish(client, topic, data):
    """
    Publishes python dict data to a specific topic in JSON and prints it out
    client: MQTT client object
    topic:  MQTT topic eg. '/v3/wireless-module/<id>/start'
    data:   Python dict containing the data to be published on the topic
    """
    # Generate JSON from the python dict
    json_data = json.dumps(data)

    # Publish the data over MQTT
    client.publish(topic, json_data)
    print(topic, "--> ", json_data)


def start_modules(args):
    """ Send the a fake filename on the start channel to start the appropriate
    module"""

    if args.id is None:
        for i in range(1, 4):
            publish(client, "/v3/wireless-module/" + str(i) + "/start", {
                "filename": "M" + str(i)
                + "_" + str(round(time.time()))
                + ".csv"
            })
        print('\nstarted module 1\nstarted module 2\nstarted module 3\n')

    else:
        publish(client, "/v3/wireless-module/" + str(args.id) + "/start", {
            "filename": "M" + str(args.id)
            + "_" + str(round(time.time()))
            + ".csv"
        })
        print('started module ' + str(args.id) + '\n')


def stop_modules(args):
    """ Sends a null message on the stop channel for all of the modules to
    stop"""

    print()  # Newline for clarity
    for i in range(1, 4):
        publish(client, "/v3/wireless-module/" + str(i) + "/stop", {})
    print('\nstopped module 1\nstopped module 2\nstopped module 3')


def start_publishing(client, args):
    print("\npublishing started...")
    start_modules(args)
    send_fake_data(client, args.time, args.rate, args.id)
    stop_modules(args)
    print("\npublishing finished")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected Sucessfully! Result code: " + str(rc))
    else:
        print("Something went wrong! Result code: " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload.decode("utf-8")))


if __name__ == "__main__":
    args = parser.parse_args()
    broker_address = args.host
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(broker_address)
    client.loop_start()
    start_publishing(client, args)
    client.loop_stop()
