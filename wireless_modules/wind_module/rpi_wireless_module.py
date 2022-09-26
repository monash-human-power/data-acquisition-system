from paho.mqtt import client as mqtt_client
import asyncio
import random
import json
import time


class WirelessModule:
    """
    A class structure to read and collate data from different sensors into a dictionary and send through MQTT.
    """

    def __init__(self, module_id, mqtt_broker):
        """
        Initialise the wireless module.
        :param module_id: An integer representing the wireless module number.
        :param battery_reader: A `BatteryReader` class to read the battery voltage from.
        """
        self.sensors = []
        
        self.pub_data_topic = "/v3/wireless_module/{}/data".format(module_id)
        
        self.sub_start_topic = "/v3/wireless_module/{}/start".format(module_id)
        self.sub_stop_topic = "/v3/wireless_module/{}/stop".format(module_id)
        
        self.status_topic = "/v3/wireless_module/{}/status".format(module_id)
        
        self.start_publish = False
        self.mqtt_broker = mqtt_broker
        last_will_payload = {"online": False}
        
        # Generate a unique client_id used to set up MQTT Client
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
    
    
    def sub_cb(self, topic, msg):
        """
        Process any message received from one of the subscribed topics.
        :param topic: The topic on which the message is received.
        :param msg: The message received.
        """
        print("Successfully received message: ", msg, "on:", topic)

        if topic == self.sub_start_topic:
            self.start_publish = True
        elif topic == self.sub_stop_topic:
            self.start_publish = False
    

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc))


    def on_message(client, userdata, msg):
        print(msg.topic + " " + str(msg.payload.decode("utf-8")))
    
    
    async def wait_for_start(self):
        """
        Asynchronously blocks until publishing is started.
        If at the time of calling the function the module is not publishing,
        each sensor will be told to start when publishing begins.
        """
        MS_TO_SEC = 1/1000
        
        if not self.start_publish:
            print("Waiting for start message...")
            
            while not self.start_publish:
                self.sub_cb = self.sub_cb
                self.mqtt.on_message = self.on_message
                await asyncio.sleep(100*MS_TO_SEC)
            
            # start message received, tell sensors to start
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
        
        # get millisecond counter and initialise to some previous time to start data publication immediately
        prev_data_sent = time.time_ns()*NS_TO_MS - interval
        
        while True:
            await self.wait_for_start()
            
            # compute the time difference since the last sensor data was read
            time_taken = time.time_ns()*NS_TO_MS - prev_data_sent
            await asyncio.sleep((interval-time_taken)*MS_TO_SEC)
            prev_data_sent = time.time_ns()*NS_TO_MS
            
            # get sensor data
            sensor_data = self._read_sensors()
            
            # publish sensor data
            self.mqtt.publish(self.pub_data_topic, json.dumps(sensor_data))
            print("MQTT data sent: {} on {}".format(sensor_data, self.pub_data_topic))
            print("\n")
            
            self.mqtt.on_message = self.on_message
            self.mqtt.on_connect = self.on_connect
        

    async def run(self, data_interval=1):
        """
        Start running the wireless module. Connect to MQTT and start the data loop.
        :param data_interval: An integer representing the number of seconds to wait before sending data.
        """
        # TODO
