import time
import argparse
import json
import paho.mqtt.client as mqtt

# my library
from MockSensor import MockSensor

parser = argparse.ArgumentParser(
    description='MQTT wireless sensor test script that sends fake data',
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
    '--host', action='store', type=str, default="192.168.100.100",
    help="""Address of the MQTT broker. If nothing is selected it will
    default to 192.168.100.100.""")
parser.add_argument(
    '--id', action='store', type=int, default=None,
    help="""Specify the sensor to produce fake data. eg. --id 1 specifies that
    sensor 1 only produces data. If nothing is given all sensors will be
    active.""")

# Generate the fake sensors with average values
s_steering_angle = MockSensor(10)
s_c02 = MockSensor(325)
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
s_GPS = MockSensor(("speed", 50),
                   ("satellites", 10),
                   ("latitude", 25),
                   ("longitude", 25),
                   ("altitude", 50),
                   ("course", 0))


def send_fake_data(client, duration, rate, sensor_ID):
    """ Send artificial data over MQTT for each sensor chanel. Sends [rate] per
    second for [duration] seconds"""

    start_time = round(time.time(), 2)

    while True:
        current_time = round(time.time(), 2)
        total_time = round(current_time - start_time, 2)
        print()     # Newline for clarity

        # Wireless Sensor 1 (Middle)
        if sensor_ID == 1 or sensor_ID is None:
            sensor_data = {
                            "filename":         "test-file.csv",
                            "temperature":      s_temperature.get_value(),
                            "humidity":         s_humidity.get_value(),
                            "steeringAngle":    s_steering_angle.get_value()
                          }
            battery_data = {"percentage": s_battery.get_value()}

            sensor_topic = "v3/wireless-sensor/1/data"
            battery_topic = "v3/wireless-sensor/1/battery"

            publish(client, sensor_topic, sensor_data)
            publish(client, battery_topic, battery_data)

        # Wireless Sensor 2 (Back)
        if sensor_ID == 2 or sensor_ID is None:
            sensor_data = {
                    "filename":         "test-file.csv",
                    "co2":              s_c02.get_value(),
                    "temperature":      s_temperature.get_value(),
                    "humidity":         s_humidity.get_value(),
                    "accelerometer":    s_accelerometer.get_value(),
                    "gyroscope":        s_gyroscope.get_value()
                   }
            battery_data = {"percentage": s_battery.get_value()}

            sensor_topic = "v3/wireless-sensor/2/data"
            battery_topic = "v3/wireless-sensor/2/battery"

            publish(client, sensor_topic, sensor_data)
            publish(client, battery_topic, battery_data)

        # Wireless Sensor 3 (Front)
        if sensor_ID == 3 or sensor_ID is None:
            sensor_data = {
                    "filename":         "test-file.csv",
                    "co2":              s_c02.get_value(),
                    "reedVelocity":     s_reed_velocity.get_value(),
                    "gps":              s_GPS.get_value(),
                   }
            battery_data = {"percentage": s_battery.get_value()}

            sensor_topic = "v3/wireless-sensor/2/data"
            battery_topic = "v3/wireless-sensor/2/battery"

            publish(client, sensor_topic, sensor_data)
            publish(client, battery_topic, battery_data)

        time.sleep(1/rate)
        if total_time >= duration:
            break


def publish(client, topic, data):
    """
    Publishes python dict data to a specific topic in JSON and prints it out
    client: MQTT client object
    topic:  MQTT topic eg. '/v3/wireless-module/<id>/start'
    data:   python dict containin the data to be published on the topic
    """
    # generate JSON from the python dict
    JSON_data = json.dumps(data)

    # publish the data over MQTT
    client.publish(topic, JSON_data)
    print(topic, "--> ", JSON_data)


def start_publishing(client, args):
    print("publishing started...")
    send_fake_data(client, args.time, args.rate, args.id)
    print("publishing finished")


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
