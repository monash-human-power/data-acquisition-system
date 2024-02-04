import time
import json
from paho.mqtt import client

import os
from dotenv import load_dotenv


class LapTimer():
    """
    Timer that publishes information on every lap completed by vehicle.
    """
    def __init__(self, broker_id = "local-host", username = None, password = None):
        """
        Initialisation

        Paramaters
            broker_id: The hostname or IP of the MQTT broker.
            username: The username for MQTT broker.
            password: The password for MQTT broker.

        Attributes
            broker_id: The hostname or IP of the MQTT broker.
            username: The username for MQTT broker
            password: The password for MQTT broker.

            last_lap_time: Start time of current lap/ Stop time of previous lap.
            last_distance: Total distance travelled so far (given by most recent ant+ post).
            last_lap_distance: Total distance travelled at start of current lap/end of previous lap.
            lap_number: Number of lap currently being completed.

            ant_topic: MQTT topic for ant+ information.
            lap_topic: MQTT topic for lap triggers.
            lap_data_topic: MQTT topic for lap information.
            self.topics: List of MQTT topics to subscribe to.
        """

        self.broker_id = broker_id
        self.username = username
        self.password = password

        
        self.last_lap_time = None
        self.last_distance = None
        self.last_lap_distance = None
        self.lap_number = 1

    
        self.ant_topic = b"/v3/wireless_module/4/data"
        self.lap_topic = b"trike/lap/trigger"
        self.lap_data_topic = b"trike/lap/data"
        self.topics = [self.ant_topic, self.lap_topic]


        
    
    def lap(self):
        """ Function called whenever a lap is completed. Publishes and resets lap information. """
        if self.last_lap_time:
            lap_time = time.time() - self.last_lap_time
            lap_distance = self.last_distance - self.last_lap_distance
            lap_speed = lap_distance/lap_time
            lap_data = {
                "lapNumber": self.lap_number,
                "time": lap_time,
                "distance": lap_distance,
                "speed": lap_speed,

            }
            self.mqtt.publish(self.lap_data_topic, json.dumps(lap_data))

            self.last_lap_distance = self.last_distance
            self.last_lap_time = time.time()
            self.lap_number += 1 
        else:
            self.last_lap_time = time.time()
    
 
    def on_message(self, client, userdata, message):
        """ Callback function used to process messages from subscribed topics """
        if message.topic == self.lap_topic:
            self.lap()

        elif message.topic == self.ant_topic:
            msg_data = json.loads(str(message.payload.decode("utf-8")))
            self.last_lap_distance = msg_data["sensors"][4]["value"]



    def on_connect(self, client, userdata, flags, connection_result):
        """ Callback function used when initally connecting to MQTT broker """
        for topic in self.topics:
            self.mqtt.subscribe(topic, qos=1)


    
    def start(self):
        """ Start Lap Timer """

        self.mqtt = client.Client()

        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect

        if self.username is not None and self.password is not None:
            self.mqtt.username_pw_set(self.username, self.password)


        self.mqtt.connect(self.broker_id)
        self.mqtt.loop_start()
        while True:
            time.sleep(1)


if __name__ == "__main__": 

    # Load env variables
    load_dotenv()
    broker_id = os.getenv("BROKER_ID") 
    username = os.getenv("USERNAME") 
    password = os.getenv("PASSWORD") 
    
    LAP_TIMER = LapTimer(broker_id, username, password) 
    
    LAP_TIMER.start()