import time
import argparse
import json
import paho.mqtt.client as mqtt

from mhp.topics import WirelessModule

from das.utils import MockSensor

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
    that module 1, 2 and 25 will produce data. If nothing is given all real
    modules will be active.""")

# Generate a dict of the fake sensors with average values
sensors = {
    "steeringAngle": MockSensor(10),
    "co2": MockSensor(325),
    "temperature": MockSensor(25),
    "humidity": MockSensor(85),
    "reedVelocity": MockSensor(50),
    "reedDistance": MockSensor(1000),
    "battery": MockSensor(80),
    "accelerometer": MockSensor(("x", 90),
                                ("y", 90),
                                ("z", 90)),
    "gyroscope": MockSensor(("x", 90),
                            ("y", 90),
                            ("z", 90)),
    "gps": MockSensor(("speed", 50),
                      ("satellites", 10),
                      ("latitude", 25),
                      ("longitude", 25),
                      ("altitude", 50),
                      ("course", 0)),
    "power": MockSensor(200, percent_range=0.8),
    "cadence": MockSensor(90, percent_range=0.2),
    "heartRate": MockSensor(120),
}

# HARDCODED MODULE ONBOARD SENSORS (dict above contains the MockSensor objects)
M1_sensors = ["temperature", "humidity", "steeringAngle"]
M2_sensors = ["co2", "temperature", "humidity", "accelerometer", "gyroscope"]
M3_sensors = ["co2", "reedVelocity", "reedDistance", "gps"]
M4_sensors = ["power", "cadence", "heartRate"]
Mn_sensors = list(sensors.keys())  # For other fake module all sensors are used


def generate_module_data(module_id_num, sensor_list):
    """
    Function to generate the module in the correct dict format before turning
    it into JSON
    module_id_num:  Unique module number (int)
    sensor_list:    list of sensors as strings such as ["co2", "reedVelocity"]
    """

    # Full dict containing all of the sensor data and their type
    module_data = {
        "module-id": module_id_num,
        "sensors": []
    }

    for sensor_name in sensor_list:
        sensor_data = {
            "type": sensor_name,
            "value": sensors[sensor_name].get_value()
        }
        module_data["sensors"].append(sensor_data)

    return module_data


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
                "percentage": sensors["battery"].get_value()
            }

            module_topic = WirelessModule.data(module_id_num)
            battery_topic = WirelessModule.battery(module_id_num)

            # Publish data and battery if needed
            publish(client, module_topic, module_data)
            if publish_battery:
                publish(client, battery_topic, battery_data)

        if publish_battery:
            battery_counter += 1

        print("TIME:", current_time)
        for module_id_num in module_id_nums:
            # Wireless module 1 (Front)
            if module_id_num == 1:
                module_data = generate_module_data(module_id_num, M1_sensors)
                publish_data_and_battery(module_id_num)

            # Wireless module 2 (Middle)
            elif module_id_num == 2:
                module_data = generate_module_data(module_id_num, M2_sensors)
                publish_data_and_battery(module_id_num)

            # Wireless module 3 (Back)
            elif module_id_num == 3:
                module_data = generate_module_data(module_id_num, M3_sensors)
                publish_data_and_battery(module_id_num)

            # Wireless module 4 (ANT+ sensor/DAS.js)
            elif module_id_num == 4:
                module_data = generate_module_data(module_id_num, M4_sensors)
                publish_data_and_battery(module_id_num)

            # Wireless module n (Other random sensor)
            else:
                module_data = generate_module_data(module_id_num, Mn_sensors)
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
    client.publish(str(topic), json_data)
    print(topic, "--> ", json_data)


def start_modules(args):
    """ Sends a null message on the start channels for all of the selected
    modules to start """

    # TODO: Add possibility to make modules by importing a file or generating
    # random modules. The modules should not be hard coded to this script.
    for module_id_num in args.id:
        publish(client, WirelessModule.start(module_id_num))
        print('Started module', module_id_num)


def stop_modules(args):
    """ Sends a null message on the stop channels for all of the selected
    modules to stop """

    for module_id_num in args.id:
        publish(client, WirelessModule.stop(module_id_num))
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
