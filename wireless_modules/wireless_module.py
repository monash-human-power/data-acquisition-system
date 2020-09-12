import machine
import ubinascii
import ujson
import time
from mqtt_client import Client

try:
    import config
except FileNotFoundError:
    print('Error importing config.py, ensure a local version of config.py exists')


class WirelessModule:
    """
    A class structure to read and collate data from different sensors into a dictionary and send through MQTT
    """
    def __init__(self, module_id):
        """
        Initialises the wireless module.
        :param module_id: An integer representing the wireless module number
        """
        self.sensors = []

        self.pub_data_topic = b"/v3/wireless-module/{}/data".format(module_id)
        self.pub_low_battery = b"/v3/wireless-module/{}/low-battery".format(module_id)
        self.pub_battery_level = b"/v3/wireless-module/{}/battery".format(module_id)

        self.sub_start_topic = b"/v3/wireless-module/{}/start".format(module_id)
        self.sub_stop_topic = b"/v3/wireless-module/{}/stop".format(module_id)

        self.start_publish = False

        # Generate a unique client_id used to set up MQTT Client
        client_id = ubinascii.hexlify(machine.unique_id())
        self.mqtt = Client(client_id, config.MQTT_BROKER)

    def add_sensors(self, sensor_arr):
        """
        Store instances of sensor class.
        :param sensor_arr: An array of sensor class instances.
        """
        self.sensors = sensor_arr

    def _read_sensors(self):
        """
        Reads sensor data from each sensor object stored within this class instance.
        :return: A dictionary of all the sensor types and their corresponding sensor reading/s
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
        Method to process any message received from one of the subscribed topics.
        :param topic: The topic on which the message is received
        :param msg: The message received
        """
        print("Successfully received message: ", msg, "on:", topic)
        if topic == self.sub_start_topic:
            self.start_publish = True
        elif topic == self.sub_stop_topic:
            self.start_publish = False

    def run(self, data_rate=1):
        """
        Start the wireless module process: Wait for start message, publish sensor data when start message
        received and continuously check for a stop message - after which the process is repeated.
        :param data_rate: Integer representing number of seconds to wait before reading and sending data
        """
        ms_to_sec = 1 / 1000

        sub_topics = [self.sub_start_topic, self.sub_stop_topic]
        self.mqtt.connect_and_subscribe(sub_topics, self.sub_cb)

        while True:
            print("waiting for message")
            self.mqtt.wait_for_message()

            # get millisecond counter
            start = time.ticks_ms()

            while self.start_publish:
                data = self._read_sensors()
                print("-------Publishing--------")

                # compute time difference
                time_taken = time.ticks_diff(time.ticks_ms(), start) * ms_to_sec

                time.sleep(data_rate - time_taken)

                self.mqtt.publish(self.pub_data_topic, ujson.dumps(data))
                start = time.ticks_ms()
                print("MQTT data sent: {} on {}".format(data, self.pub_data_topic))

                self.mqtt.check_for_message()
