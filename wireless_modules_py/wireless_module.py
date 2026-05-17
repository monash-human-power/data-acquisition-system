from paho.mqtt import client as mqtt_client
import json
import random

class WirelessModule:

    def __init__(self, module_id):

        # -----------------------------------------
        # MQTT TOPICS
        # -----------------------------------------
        # Topics are like communication channels.
        # Devices can publish OR subscribe to them.
        #
        # Example:
        # "car/sensors/data"
        #
        # Any client subscribed to this topic
        # will receive messages published to it.
        # -----------------------------------------

        self.pub_data_topic = f"module/{module_id}/data"
        self.start_topic = "system/start"
        self.status_topic = f"module/{module_id}/status"

        # Store sensors connected to this module
        self.sensors = []

        # Used to control when data starts sending
        self.start_publish = False

        # -----------------------------------------
        # MQTT CLIENT SETUP
        # -----------------------------------------
        # Every MQTT device needs a unique ID
        # to connect to the broker.
        # -----------------------------------------

        client_id = f'python-mqtt-{random.randint(0,1000)}'

        # Create MQTT client
        self.mqtt = mqtt_client.Client(client_id)

        # -----------------------------------------
        # LAST WILL MESSAGE
        # -----------------------------------------
        # If this device disconnects unexpectedly,
        # the broker automatically publishes:
        # {"online": False}
        #
        # Useful for monitoring device health.
        # -----------------------------------------

        last_will_payload = {"online": False}

        self.mqtt.will_set(
            self.status_topic,
            json.dumps(last_will_payload)
        )

    def add_sensors(self, sensor_arr):

        # Store sensor objects
        self.sensors = sensor_arr

    def _read_sensors(self):

        # -----------------------------------------
        # READ SENSOR DATA
        # -----------------------------------------
        # Collect readings from all sensors
        # into a single dictionary.
        # -----------------------------------------

        readings = {"sensors": []}

        for sensor in self.sensors:
            sensor_data = sensor.read()

            for data in sensor_data:
                readings["sensors"].append(data)

        return readings

    def on_connect(self, client, userdata, flags, rc):

        # -----------------------------------------
        # CONNECTION CALLBACK
        # -----------------------------------------
        # Runs when device connects to MQTT broker.
        #
        # Broker = central server that routes
        # messages between devices.
        # -----------------------------------------

        print(f"Connected with result code {rc}")

    def on_message(self, client, userdata, message):

        # -----------------------------------------
        # SUBSCRIBER BEHAVIOUR
        # -----------------------------------------
        # This function runs whenever a subscribed
        # topic receives a message.
        # -----------------------------------------

        print(
            f"Received message: "
            f"{message.payload.decode()} "
            f"on topic {message.topic}"
        )

        # Example:
        # If system/start receives:
        # {"start": true}
        #
        # Begin publishing sensor data.

        if message.topic == self.start_topic:

            msg_data = json.loads(
                message.payload.decode()
            )

            self.start_publish = msg_data["start"]

    async def start_data_loop(self):

        # -----------------------------------------
        # PUBLISHER LOOP
        # -----------------------------------------
        # Continuously:
        # 1. Read sensors
        # 2. Publish sensor data
        #
        # MQTT uses a lightweight publish-subscribe
        # model ideal for IoT systems.
        # -----------------------------------------

        while True:

            if self.start_publish:

                # Read all sensor values
                sensor_data = self._read_sensors()

                # ---------------------------------
                # PUBLISH MESSAGE
                # ---------------------------------
                # Send JSON sensor data to broker.
                #
                # Any subscribed client receives it.
                # ---------------------------------

                self.mqtt.publish(
                    self.pub_data_topic,
                    json.dumps(sensor_data)
                )

                print(
                    f"Published data to "
                    f"{self.pub_data_topic}"
                )

    async def run(self):

        # -----------------------------------------
        # CONNECT TO MQTT BROKER
        # -----------------------------------------
        # Examples:
        # - Mosquitto
        # - HiveMQ
        # - AWS IoT Core
        #
        # The broker handles all message routing.
        # -----------------------------------------

        self.mqtt.connect("broker_ip_address")

        # -----------------------------------------
        # SUBSCRIBE TO TOPIC
        # -----------------------------------------
        # This device listens for start commands.
        # -----------------------------------------

        self.mqtt.subscribe(self.start_topic)

        # Assign callback functions
        self.mqtt.on_connect = self.on_connect
        self.mqtt.on_message = self.on_message

        # Start MQTT background networking loop
        self.mqtt.loop_start()

        # Start publishing sensor data
        await self.start_data_loop()
