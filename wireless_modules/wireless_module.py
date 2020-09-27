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
    def __init__(self, module_id, voltage_factor, battery_pin=machine.Pin(33)):
        """
        Initialises the wireless module.
        :param module_id: An integer representing the wireless module number.
        :param battery_pin: A Pin object of the board pin connected to the middle node of the voltage divider connecting
        the battery and the ESP32
        :param voltage_factor: A float representing the ratio {(Total resistance):(Resistance between battery_pin and
        ground)}
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

        # Set up variables used to calculate battery voltage
        self.adc_battery_pin = machine.ADC(battery_pin)
        self.adc_resolution = 4095

        # Maximum voltage detected by ADC pins on the ESP32 (Can be changed using ADC.atten() method)
        self.max_readable_voltage = 1

        # The factor to multiply the voltage at the battery pin to get the battery voltage
        self.voltage_factor = voltage_factor

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

    def _read_battery_voltage(self):
        """
        Calculates the voltage level of the battery charging this wireless module
        :return: A dictionnary with key 'percentage' and the battery voltage (an int) as the associated value
        """
        adc_value = self.adc_battery_pin.read()
        print("ADC value for the battery pin: " + str(adc_value))
        voltage_at_adc_pin = (self.max_readable_voltage * adc_value) / self.adc_resolution
        battery_voltage = voltage_at_adc_pin * self.voltage_factor

        return {"percentage": battery_voltage}

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

    def run(self, data_rate=1, battery_data_rate=1):
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
                # Publish the battery voltage of this wireless module if 5 minutes (300 seconds) have elapsed since last
                # battery read
                if time.ticks_diff(time.ticks_ms(), prev_battery_read) * ms_to_sec >= battery_data_rate:
                    battery_voltage = self._read_battery_voltage()
                    self.mqtt.publish(self.pub_battery_level, ujson.dumps(battery_voltage))

                # Publish sensor data
                sensor_data = self._read_sensors()
                print("-------Publishing Sensor Data--------")

                # compute the time difference since the last sensor data was read
                time_taken = time.ticks_diff(time.ticks_ms(), prev_data_sent) * ms_to_sec
                time.sleep(data_rate - time_taken)

                self.mqtt.publish(self.pub_data_topic, ujson.dumps(sensor_data))

                prev_data_sent = time.ticks_ms()

                print("MQTT data sent: {} on {}".format(sensor_data, self.pub_data_topic))

                self.mqtt.check_for_message()
