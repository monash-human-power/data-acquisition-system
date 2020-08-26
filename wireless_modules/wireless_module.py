"""
A class structure to read and format/collate data from different sensors into a dictionary
"""
# Note: May need to add a restart() method
import ujson
import utime
from mqtt_client import Client


class WirelessModule:
    def __init__(self, id, broker, start_topic, stop_topic, pub_topic):
        """
        Initialises the wireless module
        :param id: A string representing the mqtt client id
        :param broker: A string representing the IP address or web domain of the mqtt broker
        :param start_topic: A byte literal string of the topic to subscribe, to receive start message
        :param stop_topic: A byte literal string of the topic to subscribe, to receive stop message
        :param pub_topic: A byte literal string of the topic to publish to
        """
        self.sensors = []
        self.mqtt = Client(id, broker)
        self.start_publish = False
        self.sub_topics = [start_topic, stop_topic]
        self.pub_topic = pub_topic

    def add(self, sensor_obj):
        """
        Store an instance of a sensor class
        :param sensor_obj: An instance of the sensor class, must have a .read() method to read data
        """
        self.sensors.append(sensor_obj)

    def _read_sensors(self):
        """
        Reads sensor data from each sensor object stored within this class instance
        :return: A dictionary of all the sensor types and they're corresponding sensor reading/s
        :pre-requisite: The read() method for each sensor must return a dictionary
        """
        readings = {"sensors": []}

        for sensor in self.sensors:
            sensor_data = sensor.read()
            for data in sensor_data:
                readings["sensors"].append(data)

        return readings

    def sub_cb(self, topic, msg):
        """
        Method to process any message received from one of the subscribed topics
        :param topic: The topic on which the message is received
        :param msg: The message received
        """
        print("Successfully received message: ", msg, "on:", topic)
        if topic == self.sub_topics[0]:
            self.start_publish = True
        elif topic == self.sub_topics[1]:
            self.start_publish = False

    def run(self, data_rate=1):
        """
        Starts the wireless module process of waiting for a start message, publishing sensor data when start message
        received and checking for a stop message - after which the process is repeated
        :param data_rate: Integer representing number of seconds to wait before reading and sending data
        """
        self.mqtt.connect_and_subscribe(self.sub_topics, self.sub_cb)

        while True:
            print("waiting for message")
            self.mqtt.wait_for_message()

            while self.start_publish:
                data = self._read_sensors()
                print("-------Publishing--------")
                self.mqtt.publish(self.pub_topic, ujson.dumps(data))
                print("MQTT data sent: {} on {}".format(data, self.pub_topic))

                self.mqtt.check_for_message()
                utime.sleep(data_rate)

