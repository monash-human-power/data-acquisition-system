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
        self.lap_number = 1

    
        self.ant_topic = b"/v3/wireless_module/4/data"
        self.lap_topic = b"Bla Bla"
        self.lap_data_topic = b"Bla Bla Bla"
        self.topics = [self.ant_topic, self.lap_topic]


        self.broker_id = "Bla Bla"
        client_id = "Ammanuel"
        self.mqtt = client.Client(client_id)
        pass # Set last will


        
        self.connect_to_mqtt(self.broker_id)

        
    
    def lap(self):
        if self.last_lap_time:
            lap_time = time.time() - self.last_lap_time
            lap_distance = self.last_distance - self.last_lap_distance
            lap_speed = lap_distance/lap_time
            # Do something to communicate time, speed, and distance to DAShboard
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
        
        if message.topic == self.lap_topic:
            self.lap()

        elif message.topic == self.ant_topic:
            msg_data = json.loads(str(message.payload.decode("utf-8")))
            self.last_lap_distance = msg_data["antDistance"]

    def on_connect(self, client, userdata, flags, connection_result):
        for topic in self.topics:
            self.mqtt.subscribe(topic, qos=1)


    
    def connect_to_mqtt(self, broker_id):
        self.mqtt.on_message = self.on_message
        self.mqtt.on_connect = self.on_connect

        self.mqtt.connect(broker_id)
        self.mqtt.loop_forever(retry_first_connection = True)

        
        