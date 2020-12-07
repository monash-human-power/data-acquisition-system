import paho.mqtt.client as mqtt
import time
import argparse
import json

parser = argparse.ArgumentParser(
    description='MQTT wireless module test script with dummy payloads',
    add_help=True)
parser.add_argument(
    '--module', action='store', type=int,
    default=2, help="""The module number to determine the publish and subscription topics. 
    If nothing is selected it will send on module number 2 topics.""")
parser.add_argument(
    '--host', action='store', type=str, default="localhost",
    help="""Address of the MQTT broker.""")

old_accel_data = None
old_gyro_data = None


def display_difference(old, new):
    print("Change in x: \t\t" + str(new["x"] - old["x"]))
    print("Change in y: \t\t" + str(new["y"] - old["y"]))
    print("Change in z: \t\t" + str(new["z"] - old["z"]))


def on_msg_receive(client, data, message):
    # Extract data from mqtt topic
    data = message.payload.decode('utf-8')
    data_dict = json.loads(data)
    sensors = data_dict["sensors"]

    for sensor in sensors:
        print("Type: \t" + str(sensor["type"]))
        if sensor["type"] == "accelerometer" or sensor["type"] == "gyroscope":
            new_values = sensor["value"]
            print("x value \t" + str(new_values["x"]))
            print("y value \t" + str(new_values["y"]))
            print("z value \t" + str(new_values["z"]))

            # Display change in sensor readings
            if sensor["type"] == "accelerometer":
                global old_accel_data
                # If this is not the first reading, display the change since last reading
                if old_accel_data is not None:
                    display_difference(old_accel_data, new_values)
                old_accel_data = new_values
            else:
                global old_gyro_data
                if old_gyro_data is not None:
                    display_difference(old_gyro_data, new_values)
                old_gyro_data = new_values

        else:
            print("Value: \t" + str(sensor["value"]))
        print("--------------------------")
    print("##############################")
    print("")
    return True


if __name__ == "__main__":
    client = mqtt.Client()
    args = parser.parse_args()

    MODULE_NUM = args.module

    START_TOPIC = f'/v3/wireless_module/{MODULE_NUM}/start'
    STOP_TOPIC = f'/v3/wireless_module/{MODULE_NUM}/stop'
    SUB_DATA_TOPIC = f'/v3/wireless_module/{MODULE_NUM}/data'

    # Broker domain name or IP address
    BROKER = args.host
    client.connect(BROKER)

    # Set function to call when a message from the subscribed topic is received
    client.on_message = on_msg_receive
    client.subscribe(SUB_DATA_TOPIC)

    # The start loop starts scanning for incoming messages and the stop loop stops this process.
    client.loop_start()

    # Give some time for ESP32 to "set-up"
    time.sleep(2)

    print('Sending start message')
    # QOS=1 ensures the message is received at least once
    client.publish(START_TOPIC, qos=1)

    # Wait for data to receive
    time.sleep(10)

    client.publish(STOP_TOPIC, qos=1)
    print('Sent stop message')
    client.loop_stop()
