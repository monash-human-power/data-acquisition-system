import paho.mqtt.client as mqtt
import logging
import json
import asyncio
from argparse import ArgumentParser
from utils.average import RollingAverage

# Imports from the openant Python ANT+ library
from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.bike_speed_cadence import BikeSpeed, BikeSpeedData
from openant.devices.heart_rate import HeartRate, HeartRateData
from openant.devices.power_meter import PowerMeter, PowerData
from openant.devices.common import DeviceData


parser = ArgumentParser(add_help = True, description = 'Ant-Plus MQTT Logger')

parser.add_argument('-i', '--id', help= 'Wireless sensor module ID', default = 4, type = int, action = 'store')

parser.add_argument('-a', '--host', help= 'Address of the MQTT broker. If nothing is selected it will default to http://localhost.', default = 'localhost', action = 'store')

parser.add_argument('-r', '--rate', help= 'Rate to publish data in Hz', default= 1, type = float, action = 'store')

args = parser.parse_args()
module_id = args.id
mqtt_address = args.host
rate = args.rate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f'Wireless module ID: {module_id}')

v3_start_topic = 'v3/start';
data_topic = f'/v3/wireless_module/{module_id}/data';
status_topic = f'/v3/wireless_module/{module_id}/status';

# // 406c 28mm tyre: https://www.bikecalc.com/wheel_size_math
WHEEL_CIRCUMFERENCE_M = 1.44513 # m



async def mqtt_connect():
    """
    Connect to the MQTT broker

    @returns mqtt_client: MQTT client
    """

    def on_connect(client, userdata, flags, rc):
        logger.info('Connected to MQTT broker')
        will_payload = { "online": False }
        client.will_set(topic= status_topic, payload= json.dumps(will_payload), qos= 0, retain= True)

    logger.info('Connecting to MQTT broker...')
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(host = mqtt_address)
    mqtt_client.loop_start()

    return mqtt_client


async def antplus_connect():
    """
    Connect to the ANT+ stick

    @returns ant_node: ANT+ stick instance
    """

    ant_node = Node()
    ant_node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    try:
        ant_node.start()
        logger.info('ant-plus stick initialized')
        return ant_node
    except KeyboardInterrupt:
        logger.info(f'Closing ANT+ device..."')


def on_device_data(page: int, page_name: str, data: DeviceData):
    """
    Common ANT+ data callback for all sensors

    @param data: Device data from sensor
    """
    if isinstance(data, BikeSpeedData):
        speed = data.calculate_speed(WHEEL_CIRCUMFERENCE_M)
        distance = data.calculate_distance(WHEEL_CIRCUMFERENCE_M)
        if speed:
            print(f"speed: {speed:.2f} km/h")
            print(f"distance: {speed:.2f} m")
            sensor_values["speed"] = speed
            sensor_values["distance"] = distance
    elif isinstance(data, PowerData):
        print(f"power: {data.instantaneous_power} watts")
        print(f"cadence: {data.cadence} rpm")
        sensor_values["power"] = data.instantaneous_power
        sensor_values["cadence"] = data.cadence
    elif isinstance(data, HeartRateData):
        print(f"Heart rate update {data.heart_rate} bpm")
        sensor_values["heartRate"] = data.heart_rate


async def bicycle_speed_connect(ant_plus): 
    """
    Connect to the bicycle speed sensor

    @param ant_plus: ANT+ stick instance
    """
    def on_found():
        print(f"Speed sensor attached")

    bicycle_speed_scanner = BikeSpeed(ant_plus)
    bicycle_speed_scanner.on_found = on_found
    bicycle_speed_scanner.on_device_data = on_device_data
    bicycle_speed_scanner.open_channel()
    
async def bicycle_power_connect(ant_plus):
    """
    Connect to the bicycle power sensor

    @param ant_plus: ANT+ stick instance
    """
    def on_found():
        print(f"Bicycle power sensor attached")

    bicycle_power_scanner = PowerMeter(ant_plus)
    bicycle_power_scanner.on_found = on_found
    bicycle_power_scanner.on_device_data = on_device_data
    bicycle_power_scanner.open_channel()
    
async def heart_rate_connect(ant_plus):
    """
    Connect to the heart rate sensor

    @param ant_plus: ANT+ stick instance
    """
    def on_found():
        print(f"Heart rate sensor attached")

    heart_rate_scanner = HeartRate(ant_plus)
    heart_rate_scanner.on_found = on_found
    heart_rate_scanner.on_device_data = on_device_data
    heart_rate_scanner.open_channel()


async def main():
    """
    Main function that listens and logs data from ANT+ sensors 
    """
    global power_average, sensor_values

    sensor_values = {
        "speed": 0,
        "power": 0,
        "cadence": 0,
        "heartRate": 0
    }

    power_average = RollingAverage(3000)

    is_recording = False
    online_msg = { 'online': True }

    mqtt_client = await mqtt_connect()
    ant_plus = await antplus_connect()

    # Announce we're online once ANT+ stick is also connected
    mqtt_client.publish(topic= status_topic, payload= json.dumps(online_msg), retain= True)

    mqtt_client.subscribe(v3_start_topic)
    logging.info('Waiting for messages...')

    def on_message(client, userdata, message):
        nonlocal is_recording, distance

        topic = message.topic
        payload = message.payload.decode('utf-8')

        logger.info(f'Topic fired: {topic}')

        if topic == v3_start_topic:
            msg = json.loads(payload)

            if msg.get('start'):
                is_recording = True
                sensor_values.update({"distance": 0})
                logger.info('Start publishing data')
            else:
                is_recording = False
                logger.info('Stop publishing data')
        else:
            logger.error(f'Unexpected topic: {topic}')

    mqtt_client.on_message = on_message

    await bicycle_speed_connect(ant_plus)
    await bicycle_power_connect(ant_plus)
    await heart_rate_connect(ant_plus)

    while True:
        await asyncio.sleep(1 / rate)

        if is_recording:
            speed = sensor_values["speed"]
            distance = sensor_values["distance"]
            power = round(power_average.average(), 2) if len(power_average.points) != 0 else sensor_values["power"]
            cadence = sensor_values["cadence"]
            heartRate = sensor_values["heartRate"]

            payload = {
                "sensors": [
                    {"type": "antSpeed", "value": speed} if speed else {},
                    {"type": "antDistance", "value": distance} if distance else {},
                    {"type": "power", "value": power} if power else {},
                    {"type": "cadence", "value": cadence} if cadence else {},
                    {"type": "heartRate", "value": heartRate} if heartRate else {},
                ]
            }
            payload["sensors"] = [sensor for sensor in payload["sensors"] if sensor]
            data = json.dumps(payload)
            mqtt_client.publish(topic= data_topic, payload= data)
            logger.info(f"{data_topic} -> {data}")

if __name__ == "__main__":
    asyncio.run(main())