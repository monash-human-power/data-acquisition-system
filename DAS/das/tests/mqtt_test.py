import sys
import argparse
import paho.mqtt.client as mqtt

from mhp import topics

from das.tests.das_data_generator import send_csv_data, send_fake_data

# Arguments
parser = argparse.ArgumentParser(
    description='DAS MQTT python script', add_help=True)
parser.add_argument('-t', '--time', action='store', type=int,
                    default=1, help="length of time to send data")
parser.add_argument('-r', '--rate', action='store', type=float,
                    default=0.5, help="rate of data in seconds")
parser.add_argument('--host', action='store', type=str,
                    default="localhost", help="address of the MQTT broker")
parser.add_argument('--port', action='store', type=int,
                    default=1883, help="address of the MQTT broker")
parser.add_argument('--username', action='store', type=str,
                    help="username for the MQTT broker (optional)")
parser.add_argument('--password', action='store', type=str,
                    help="password for the MQTT broker (optional)")
parser.add_argument('-f', '--file', action='store', type=str,
                    help="The csv file to replay. If not specified, makes up data.")
parser.add_argument('-s', '--speed', action='store',
                    type=float, default=1, help="Replay speed multiplier")
parser.add_argument('-j', '--jump', action='store', type=int, default=0,
                    help="Starts replaying from a specified time (in seconds)")


def start_publishing(client, args):
    print("start")
    client.publish(str(topics.BOOST.start))
    client.publish(str(topics.DAS.start))

    def send_data_func(data):
        return client.publish(str(topics.DAS.data), data)

    if args.file is None:
        send_fake_data(send_data_func, args.time, args.rate)
    else:
        send_csv_data(send_data_func, args.file, args.jump, speedup=args.speed)

    print("stop")
    client.publish(str(topics.DAS.stop))
    client.publish(str(topics.BOOST.stop))
    sys.exit(0)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))


def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload.decode("utf-8")))


if __name__ == "__main__":
    args = parser.parse_args()
    broker_address = args.host
    broker_port = args.port
    client = mqtt.Client()

    client.on_connect = on_connect
    client.on_message = on_message

    broker_username = args.username
    broker_password = args.password
    if broker_username is not None:
        client.username_pw_set(broker_username, broker_password)

    client.connect(broker_address, port=broker_port)
    start_publishing(client, args)

    client.loop_forever()
