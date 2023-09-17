import time
import json
from paho.mqtt import client


class LapTimer():
    def __init__(self):
        """
        Initialisation
        """
        self.last_lap_time = None
        self.last_distance = None
        self.last_lap_distance = None

    
        self.ant_topic = b"/v3/wireless_module/4/data"
        self.lap_topic = b"Bla Bla"
        self.broker_id = "Bla Bla"

        client_id = "Ammanuel"
        self.mqtt = client.Client(client_id)
        pass # Set last will

        
        # Don't know if this is where I am supposed to connect
        topics = [self.ant_topic, self.lap_topic]
        self.connect_to_mqtt(self.broker_id, topics)

        
    
    def lap(self):
        if self.last_lap_time:
            lap_time = time.time() - self.last_lap_time
            lap_distance = self.last_distance - self.last_lap_distance
            lap_speed = lap_distance/lap_time
            # Do something to communicate time, speed, and distance to DAShboard

            self.last_lap_distance = self.last_distance
            self.last_lap_time = time.time()
        else:
            self.last_lap_time = time.time()
    
 
    def on_message(self, client, userdata, message):
        
        if message.topic == self.lap_topic:
            self.lap()

        elif message.topic == self.ant_topic:
            msg_data = json.loads(str(message.payload.decode("utf-8")))
            self.last_lap_distance = msg_data["antDistance"]

    def connect_to_mqtt(self, broker_id, topics):
        self.mqtt.on_message = self.on_message

        self.mqtt.connect(broker_id)

        for topic in topics:
            self.mqtt.subscribe(topic, qos=1)

        