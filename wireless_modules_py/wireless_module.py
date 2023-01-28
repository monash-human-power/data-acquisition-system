from mhp import topics
import random
from paho.mqtt import client as mqtt_client
import json
import logging
import asyncio
import time
import config
import logging


class WirelessModule:
    """
    A class structure to read and collate data from different sensors into a dictionary and send through MQTT.
    """

    def __init__(self, module_id):
        """
        Initialise the wireless module.
        :param module_id: An integer representing the wireless module number.
        """
        self.sensors = []

        self.pub_data_topic = str(topics.WirelessModule.id(module_id).data)

        self.v3_start = str(topics.V3.start)

        self.status_topic = str(topics.WirelessModule.id(module_id).status)

        self.start_publish = False
        last_will_payload = {"online": False}

        # generate a unique client_id used to set up MQTT Client
        client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.mqtt = mqtt_client.Client(client_id)
        self.mqtt.will_set(self.status_topic, json.dumps(last_will_payload))


    def add_sensors(self, sensor_arr):
        """
        Store instances of Sensor class.
        :param sensor_arr: An array of Sensor class instances.
        """
        self.sensors = sensor_arr


    def _read_sensors(self):
        """
        Read sensor data from each Sensor object stored within this class instance.
        :return: A dictionary of all the sensor types and their corresponding sensor reading/s.
        :pre-requisite: The read() method for each sensor must return a dictionary.
        """
        readings = {"sensors": []}

        for sensor in self.sensors:
            sensor_data = sensor.read()
            for data in sensor_data:
                readings["sensors"].append(data)

        return readings


    def on_connect(self, client, userdata, flags, rc):
        """
        Process the broker's response to the connection request made by client.
        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or user_data_set().
        :param flags: A dictionary that contains response flags sent by the broker.
        :param rc: The connection result.
        """
        logging.debug("Connected with result code {}: {}".format(str(rc), self.rc_to_message(rc)))

        # reconnect to broker if previous connection request failed
        if rc != 0:
            logging.debug("Reconnecting...")
            client.reconnect()


    def rc_to_message(self, rc):
        """
        Convert the connection response code returned by the broker to a string message.
        :param rc: The connection response code.
        :return: A string message corresponding to the response code.
        """
        rc_messages = {
            0: "Connetion successful",
            1: "Connection refused - incorrect protocol version",
            2: "Connection refused - invalid client identifier",
            3: "Connection refused - server unavailable",
            4: "Connection refused - bad username or password",
            5: "Connection refused - not authorised"
        }

        return rc_messages.get(rc)


    def on_message(self, client, userdata, message):
        """
        Process any message received from one of the subscribed topics.
        :param client: The client instance for this callback.
        :param userdata: The private user data as set in Client() or user_data_set().
        :param message: The instance of MQTTMessage received, with members topic, payload, qos, retain.
        """
        logging.debug("Successfully received message: {} on: {}".format(
            message.payload.decode("utf-8"), message.topic))

        if message.topic == self.v3_start:
            msg_data = json.loads(str(message.payload.decode("utf-8")))
            self.start_publish = msg_data["start"]


    async def wait_for_start(self):
        """
        Asynchronously blocks until publishing is started.
        If at the time of calling the function the module is not publishing, each sensor will be told to start when publishing begins.
        """
        MS_TO_SEC = 1/1000

        if not self.start_publish:
            logging.info("Waiting for start message...")

            while not self.start_publish:
                await asyncio.sleep(100*MS_TO_SEC)

            for sensor in self.sensors:
                sensor.on_start()


    async def start_data_loop(self, interval):
        """
        Start the wireless module data publishing process: Wait for the start message,
        publish sensor data once start message is received and continuously check for the stop message - after which the process is repeated.
        :param interval: An integer representing the number of seconds to wait before sending data.
        """
        NS_TO_MS = 1000000
        SEC_TO_MS = 1000
        MS_TO_SEC = 1/1000

        interval *= SEC_TO_MS

        status = {"online": True}

        message = str.encode(json.dumps(status))
        self.mqtt.publish(self.status_topic, message, retain=True)

        prev_data_sent = time.time_ns()*NS_TO_MS - interval

        while True:
            await self.wait_for_start()

            # compute the time difference since the last sensor data was read
            time_taken = time.time_ns()*NS_TO_MS - prev_data_sent
            await asyncio.sleep((interval-time_taken)*MS_TO_SEC)
            prev_data_sent = time.time_ns()*NS_TO_MS

            # publish sensor data
            sensor_data = self._read_sensors()
            self.mqtt.publish(self.pub_data_topic, json.dumps(sensor_data))
            logging.info("MQTT data sent: {} on {}\n".format(
                sensor_data, self.pub_data_topic))


    async def run(self, data_interval=1):
        """
        Start running the wireless module. Connect to MQTT and start the data loop.
        :param data_interval: An integer representing the number of seconds to wait before sending data.
        """
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message

        # connect to broker
        self.mqtt.username_pw_set(config.USERNAME, config.PASSWORD)
        self.mqtt.connect(config.MQTT_BROKER)

        # subscribe to start topic
        sub_topics = [self.v3_start]
        for topic in sub_topics:
            self.mqtt.subscribe(topic, qos=1)
            logging.debug("Subscribed to {} topic".format(topic))

        asyncio.create_task(self.start_data_loop(data_interval))
        self.mqtt.loop_start()
