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
    A class structure to read and collate data from different sensors into a dictionary and send through MQTT.
    """
    def __init__(self, module_id, battery_reader=None):
        """
        Initialises the wireless module.
        :param module_id: An integer representing the wireless module number.
        :param battery_reader: A `BatteryReader` class to read the battery voltage from
        """
        self.sensors = []

        self.pub_sensor_topic = b"/v3/wireless_module/{}/data".format(module_id)
        self.battery_topic = b"/v3/wireless_module/{}/battery".format(module_id)

        self.sub_start_topic = b"/v3/wireless_module/{}/start".format(module_id)
        self.sub_stop_topic = b"/v3/wireless_module/{}/stop".format(module_id)

        self.start_publish = False

        # Generate a unique client_id used to set up MQTT Client
        client_id = ubinascii.hexlify(machine.unique_id())
        self.mqtt = Client(client_id, config.MQTT_BROKER)

        self.battery = battery_reader

    def add_sensors(self, sensor_arr):
        """
        Store instances of sensor class.
        :param sensor_arr: An array of sensor class instances.
        """
        self.sensors = sensor_arr

    def _read_sensors(self):
        """
        Read sensor data from each sensor object stored within this class instance.
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
        Method to process any message received from one of the subscribed topics.
        :param topic: The topic on which the message is received.
        :param msg: The message received.
        """
        print("Successfully received message: ", msg, "on:", topic)
        if topic == self.sub_start_topic:
            self.start_publish = True
        elif topic == self.sub_stop_topic:
            self.start_publish = False

    def run(self, data_rate=1, battery_data_rate=300):
        """
        Start the wireless module process: Wait for start message, publish sensor data when start message
        received and continuously check for a stop message - after which the process is repeated.
        :param data_rate: Integer representing number of seconds to wait before sending data.
        :param battery_data_rate: Integer representing number of seconds to wait before sending battery voltage data
        """
        ms_to_sec = 1 / 1000

        sub_topics = [self.sub_start_topic, self.sub_stop_topic]
        self.mqtt.connect_and_subscribe(sub_topics, self.sub_cb)

        while True:
            print("waiting for message")
            self.mqtt.wait_for_message()

            # get millisecond counter
            prev_data_sent = time.ticks_ms()
            prev_battery_read = time.ticks_ms()

            while self.start_publish:
                # Publish the battery voltage of this wireless module if the given delay (refer to `battery_data_rate`)
                # has elapsed
                time_since_last_battery_read = time.ticks_diff(time.ticks_ms(), prev_battery_read) * ms_to_sec
                if time_since_last_battery_read >= battery_data_rate and self.battery is not None:
                    battery_voltage = self.battery.read()
                    self.mqtt.publish(self.battery_topic, ujson.dumps(battery_voltage))

                # Publish sensor data
                sensor_data = self._read_sensors()

                # compute the time difference since the last sensor data was read
                time_taken = time.ticks_diff(time.ticks_ms(), prev_data_sent) * ms_to_sec
                time.sleep(data_rate - time_taken)

                self.mqtt.publish(self.pub_sensor_topic, ujson.dumps(sensor_data))
                prev_data_sent = time.ticks_ms()

                print("MQTT data sent: {} on {}".format(sensor_data, self.pub_sensor_topic))
                self.mqtt.check_for_message()
