import time
import argparse
import json
import paho.mqtt.client as mqtt
from MockSensor import MockSensor
import topics

parser = argparse.ArgumentParser(
    description='MQTT wireless module test script that sends fake data',
    add_help=True)
parser.add_argument(
    '-t', '--time', action='store', type=int,
    default=float('Inf'), help="""Length of time to send data in seconds
    (duration). If nothing is selected it will continuously send out data.""")
parser.add_argument(
    '-r', '--rate', action='store', type=float, default=1,
    help="""Rate of data in data sent per second. Default is 1 data pack sent
    per second.""")
parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to localhost.""")
parser.add_argument(
    '-i', '--id', action='store', nargs='+', type=int, default=[1, 2, 3, 4],
    help="""Specify the module to produce fake data. eg. --id 1 2 25 specifies
    that module 1, 2 and 25 will produce data. If nothing is given all modules
    will be active.""")

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


def send_fake_data(client, duration, rate, module_id_nums):
    """ Send artificial data over MQTT for each module chanel. Sends [rate] per
    second for [duration] seconds

    client:         MQTT client
    duration:       How long in seconds the script should output data before
                    terminating
    rate:           Frequency of sending out data in Hz
    module_id_nums: List of ints containing module ids that are enabled for the
                    mock test
    """

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

        def publish_data_and_battery(module_id_num):
            battery_data = {
                "module-id": module_id_num,
                "percentage": s_battery.get_value()
            }

            module_topic = topics.WirelessModule.data(module_id_num)
            battery_topic = topics.WirelessModule.battery(module_id_num)

            # Publish data and battery if needed
            publish(client, module_topic, module_data)
            if publish_battery:
                publish(client, battery_topic, battery_data)

        if publish_battery:
            battery_counter += 1

        print("TIME:", current_time)
        for module_id_num in module_id_nums:
            # Wireless module 1 (Middle)
            if module_id_num == 1:
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
                publish_data_and_battery(module_id_num)

            # Wireless module 2 (Back)
            elif module_id_num == 2:
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
                publish_data_and_battery(module_id_num)

            # Wireless module 3 (Front)
            elif module_id_num == 3:
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
                publish_data_and_battery(module_id_num)

            # For other 'fake modules'
            else:
                module_data = {
                                "sensors": [
                                    {
                                        "type": "co2",
                                        "value": s_co2.get_value()
                                    }
                                 ]
                              }
                publish_data_and_battery(module_id_num)

        print()  # Newline for clarity
        time.sleep(1/rate)


def publish(client, topic, data={}):
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
    """ Sends a null message on the start channels for all of the selected
    modules to start """

    # TODO: Add posibility to make modules by importing a file or generating
    # random modules. The modules should not be hard coded to this script.
    for module_id_num in args.id:
        publish(client, topics.WirelessModule.start(module_id_num))
        print('Started module', module_id_num)


def stop_modules(args):
    """ Sends a null message on the stop channels for all of the selected
    modules to stop """

    for module_id_num in args.id:
        publish(client, topics.WirelessModule.stop(module_id_num))
        print('Stopped module', module_id_num)


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
