import uasyncio as asyncio
import machine
import ubinascii
import ujson
import json
import sys
import time

from mqtt_client import Client
from status_led import WmState

try:
    import config
except FileNotFoundError:
    print("Error importing config.py, ensure a local version of config.py exists")

LOW_BATTERY_THRESHOLD = 3.3


class WirelessModule:
    """
    A class structure to read and collate data from different sensors into a dictionary and send through MQTT.
    """

    def __init__(self, module_id, battery_reader=None, status_led=None):
        """
        Initialises the wireless module.
        :param module_id: An integer representing the wireless module number.
        :param battery_reader: A `BatteryReader` class to read the battery voltage from
        """
        self.sensors = []

        self.pub_data_topic = b"/v3/wireless_module/{}/data".format(module_id)
        self.battery_topic = b"/v3/wireless_module/{}/battery".format(module_id)

        self.v3_start = b"v3/start"

        self.status_topic = b"/v3/wireless_module/{}/status".format(module_id)

        self.start_publish = False
        last_will_payload = {"online": False}

        # Generate a unique client_id used to set up MQTT Client
        client_id = ubinascii.hexlify(machine.unique_id())
        self.mqtt = Client(client_id, config.MQTT_BROKER)
        self.mqtt.set_last_will(self.status_topic, ujson.dumps(last_will_payload))

        self.battery = battery_reader
        self.status_led = status_led

        asyncio.get_event_loop().set_exception_handler(self.error_handler)

    def error_handler(self, _loop, context):
        self.status_led.set_state(WmState.Error)
        print("An error occured in a uasyncio task!")
        print(context["message"])
        sys.print_exception(context["exception"])

        # FIXME: A nicer solution would be to restart all running tasks rather than reset

        print("Resetting in 5 seconds...")

        time.sleep(5)
        machine.reset()

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

        if topic == self.v3_start:
            msg_data = json.loads(str(msg.decode("utf-8")))
            self.start_publish = msg_data["start"]

    async def start_battery_loop(self, interval):
        """
        Start publishing the battery voltage and if required show the battery warning
        on the status LED.
        :param interval: Integer representing number of seconds to wait before sending battery voltage data
        """
        if self.battery is None:
            return

        while True:
            battery_voltage = self.battery.read()
            if self.mqtt.connected:
                self.mqtt.publish(
                    self.battery_topic, ujson.dumps(battery_voltage), retain=True
                )
            self.status_led.set_warning_state(
                WmState.LowBattery
                if battery_voltage["voltage"] <= LOW_BATTERY_THRESHOLD
                else None
            )
            await asyncio.sleep(interval)

    async def wait_for_start(self):
        """
        Asynchronously blocks until publishing is started.
        If at the time of calling the function the module is not publishing,
        each sensor will be told to start when publishing begins.
        """
        if not self.start_publish:
            print("Waiting for start message...")

            while not self.start_publish:
                self.status_led.set_state(WmState.Idle)
                self.mqtt.check_for_message()
                await asyncio.sleep_ms(100)

            self.status_led.set_state(WmState.Publishing)

            # Start message received, tell sensors to start
            for sensor in self.sensors:
                sensor.on_start()
        
        #Fix for changing LED when a true is retained
        if self.start_publish and self.status_led.state != WmState.Publishing:
            self.status_led.set_state(WmState.Publishing)


    async def start_data_loop(self, interval):
        """
        Start the wireless module data publishing process: Wait for start message,
        publish sensor data when start message received and continuously check for a
        stop message - after which the process is repeated.
        :param interval: Integer representing number of seconds to wait before sending data.
        """
        secs_to_ms = 1000
        interval *= secs_to_ms

        status = {"online": True}
        self.mqtt.publish(self.status_topic, ujson.dumps(status), retain=True)

        # get millisecond counter and initialise to some previous time to start data publication immediately
        prev_data_sent = time.ticks_ms() - interval

        while True:
            await self.wait_for_start()

            # Compute the time difference since the last sensor data was read
            time_taken = time.ticks_diff(time.ticks_ms(), prev_data_sent)
            await asyncio.sleep_ms(interval - time_taken)
            prev_data_sent = time.ticks_ms()

            # Get and publish sensor data
            sensor_data = self._read_sensors()

            self.mqtt.publish(self.pub_data_topic, ujson.dumps(sensor_data))
            print("MQTT data sent: {} on {}".format(sensor_data, self.pub_data_topic))

            self.mqtt.check_for_message()

    async def run(self, data_interval=1, battery_data_interval=300):
        """
        Start running the wireless module. Connects to MQTT and starts the data and battery loops.
        :param data_interval: Integer representing number of seconds to wait before sending data.
        :param battery_interval: Integer representing number of seconds to wait before sending battery voltage data
        """
        # Start publishing battery data straight away
        asyncio.create_task(self.start_battery_loop(battery_data_interval))

        # Attempt to connect to MQTT (will block until successful)
        self.status_led.set_state(WmState.ConnectingToMqtt)
        sub_topics = [self.v3_start]
        await self.mqtt.connect_and_subscribe(sub_topics, self.sub_cb)

        # Start the main publishing loop
        asyncio.create_task(self.start_data_loop(data_interval))
