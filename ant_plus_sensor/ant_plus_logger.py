# IMPORTS
import paho.mqtt.client as mqtt
from argparse import ArgumentParser
import logging
from utils.average import RollingAverage

import json
import asyncio

# EXAMPLE USAGE OF NEW PYTHON-ANT LIBRARY
from ant.plus.heartrate import *

# TODO
# Required to detect speed sensor.
# The GitHub code has a SpeedScanner class which isn't accessible here for some reason.
# It uses a deviceType of 0x7b (SpeedCadenceScanner uses 0x79), and replacing it seems to work.
# Ant.SpeedCadenceScanner.deviceType = 0x7b;

parser = ArgumentParser(add_help = True, description = 'Ant-Plus MQTT Logger')

parser.add_argument('-i', '--id', help= 'Wireless sensor module ID', default = 4, type = int, action = 'store')

parser.add_argument('-a', '--host', help= 'Address of the MQTT broker. If nothing is selected it will default to http://localhost.', default = 'http://localhost', action = 'store')

parser.add_argument('-r', '--rate', help= 'Rate to publish data in Hz', default= 1, type = float, action = 'store')

args = parser.parse_args()
module_id = args.id
mqtt_address = args.host

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f'Wireless module ID: {module_id}')

v3_start_topic = 'v3/start';
data_topic = f'/v3/wireless_module/${module_id}/data';
status_topic = f'/v3/wireless_module/${module_id}/status';


# // 406c 28mm tyre: https://www.bikecalc.com/wheel_size_math
wheelCircumference = 1.44513 # m


##############################
# Connect to the MQTT broker #
##############################

async def mqtt_connect():
    """
    Connect to the MQTT broker

    @return Promise of MQTT client
    """

    def on_connect(client, userdata, flags, rc):
        logger.info(f'Connected to MQTT broker')
        will_payload = { "online": False }
        client.will_set(topic= status_topic, payload= json.dumps(will_payload), qos= 0, retain= True)

    logger.info('Connecting to MQTT broker...')
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.connect_async(host = mqtt_address)
    mqtt_client.loop_start()

    return mqtt_client


#############################
# Connect to the ANT+ stick #
#############################

async def antplus_connect():
    pass


#######################################
# Connect to the bicycle speed sensor #
#######################################

async def bicycle_speed_connect(antPlus):
    pass


#######################################
# Connect to the bicycle power sensor #
#######################################

async def bicycle_power_connect(antPlus):
    pass

####################################
# Connect to the heart rate sensor #
####################################

async def heart_rate_connect(antPlus):
    pass


########
# Main #
########

async def main():
    isRecording = False
    speed = 0
    # The number of wheel revolutions according to the sensor when we start recording
    startWheelRevolutions = None
    distance = 0
    powerAverage = RollingAverage(3000)
    cadence = 0
    heartRate = 0
    onlineMsg = { 'online': True }

    mqttClient = await mqtt_connect()
    antPlus = await antplus_connect()

    # Announce we're online once ANT+ stick is also connected
    mqttClient.publish(topic= status_topic, payload= json.dumps(onlineMsg), retain= True)

    mqttClient.subscribe(v3_start_topic)
    logging.info('Waiting for messages...')

    def on_message(client, userdata, message):
        nonlocal isRecording, distance, startWheelRevolutions

        topic = message.topic
        payload = message.payload.decode('utf-8')

        logger.info(f'Topic fired: {topic}')

        if topic == v3_start_topic:
            msg = json.loads(payload)

            if msg.get('start'):
                isRecording = True
                distance = 0
                startWheelRevolutions = None
                logger.info('Start publishing data')
            else:
                isRecording = False
                logger.info('Stop publishing data')
        else:
            logger.error(f'Unexpected topic: {topic}')

    mqttClient.on_message = on_message

    # TODO


if __name__ == "__main__":
    asyncio.run(main())