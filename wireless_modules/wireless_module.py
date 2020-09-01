"""
A class structure to read and collate data from different sensors into a dictionary and send through MQTT
"""
# Note: May need to add a restart() method later on
import ujson
import utime
from mqtt_client import Client


class WirelessModule:
    def __init__(self, id, broker):
        """
        Initialises the wireless module
        :param id: A string representing the mqtt client id
        :param broker: A string representing the IP address or web domain of the mqtt broker
        """
        self.sensors = None
        self.start_publish = False
        self.sub_topics = []
        self.pub_topics = []

        self.mqtt = Client(id, broker)

    def set_sub_topics(self, start_topic, stop_topic):
        """
        Set the MQTT topics to subscribe to. Ensure the order of input is correct.
        :param start_topic: A byte literal of the topic to wait for the start message
        :param stop_topic: A byte literal of the topic to check for the stop message
        """
        self.sub_topics.append(start_topic)
        self.sub_topics.append(stop_topic)

    def set_pub_topics(self, data_topic, battery_topic, low_battery_topic):
        """
        Set the MQTT Topics to publish to. Order of input is important.
        :param data_topic: A byte literal representing the topic to publish sensor data to
        :param battery_topic: A byte literal representing the topic to publish battery percentage to
        :param low_battery_topic: A byte literal representing the topic to publish to when battery is low
        :return:
        """
        self.pub_topics.append(data_topic)
        self.pub_topics.append(battery_topic)
        self.pub_topics.append(low_battery_topic)

    def add_sensors(self, sensor_arr):
        """
        Store an instance of a sensor class
        :param sensor_arr: An array of sensor class instances, each class have a .read() method to read data
        """
        self.sensors = sensor_arr

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
        Starts the wireless module process: Waits for a start message, publishes sensor data when start message is
        received and continuously checks for a stop message - after which the process is repeated
        :param data_rate: Integer representing number of seconds to wait before reading and sending data
        """
        self.mqtt.connect_and_subscribe(self.sub_topics, self.sub_cb)

        while True:
            print("waiting for message")
            self.mqtt.wait_for_message()

            while self.start_publish:
                data = self._read_sensors()
                print("-------Publishing--------")
                self.mqtt.publish(self.pub_topics[0], ujson.dumps(data))
                print("MQTT data sent: {} on {}".format(data, self.pub_topics[0]))

                self.mqtt.check_for_message()
                utime.sleep(data_rate)

