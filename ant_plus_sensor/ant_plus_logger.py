# IMPORTS
import paho.mqtt.client as mqtt
from argparse import ArgumentParser
import logging
from utils.average import RollingAverage

import json
import asyncio

# Imports from new Python ANT library
from ant.core import driver, exceptions
from ant.core.node import Node, Network
from ant.core.constants import NETWORK_KEY_ANT_PLUS, NETWORK_NUMBER_PUBLIC
from ant.plus.power import *
from ant.plus.heartrate import *
from ant.plus.bikeTrainer import *


parser = ArgumentParser(add_help = True, description = 'Ant-Plus MQTT Logger')

parser.add_argument('-i', '--id', help= 'Wireless sensor module ID', default = 4, type = int, action = 'store')

parser.add_argument('-a', '--host', help= 'Address of the MQTT broker. If nothing is selected it will default to http://localhost.', default = 'http://localhost', action = 'store')

parser.add_argument('-r', '--rate', help= 'Rate to publish data in Hz', default= 1, type = float, action = 'store')

args = parser.parse_args()
module_id = args.id
mqtt_address = args.host
rate = args.rate

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

    @return MQTT client
    """

    def on_connect(client, userdata, flags, rc):
        logger.info('Connected to MQTT broker')
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
    """
    Connect to the ANT+ stick

    @return ANT+ stick instance
    """

    logger.info('Finding ant-plus USB...')
    ant_node = Node(driver.USB2Driver(log=True, debug=True, idProduct=0x1009))

    try:
        ant_node.start()
        network = Network(key=NETWORK_KEY_ANT_PLUS, name='N:ANT+')
        ant_node.setNetworkKey(NETWORK_NUMBER_PUBLIC, network)
        logger.info('ant-plus stick initialized')
    except exceptions.ANTException as err:
        logger.info(f'Could not start ANT.\n{err}')

    return (ant_node, network)


###################################################
#  Common ANT Callbacks for all sensors           #
###################################################

def device_paired(device_profile, channel_id):
    print(f'Connected to {device_profile.name} ({channel_id.deviceNumber})')

def search_timed_out(device_profile):
    print(f'Could not connect to {device_profile.name}')

def channel_closed(device_profile):
    print(f'Channel closed for {device_profile.name}')



#############################################################
# Connect to the bicycle speed sensor (uses a bike trainer) #
#############################################################

#-------------------------------------------------#
#  ANT Callbacks for bicycle speed sensor         #
#-------------------------------------------------#

def device_paired(device_profile, channel_id):
    print(f'Connected to {device_profile.name} ({channel_id.deviceNumber})')

def search_timed_out(device_profile):
    print(f'Could not connect to {device_profile.name}')

def channel_closed(device_profile):
    print(f'Channel closed for {device_profile.name}')

def bike_Trainer(elapsedTime, distanceTraveled, instantaneousSpeed, kmSpeed, cadence, power):
    print(f"Speed: {kmSpeed} km/h, Cadence: {cadence}, Power: {power}")

#-------------------------------------------------#
#  Function for connecting bicycle speed sensor   #
#-------------------------------------------------#

async def bicycle_speed_connect(antPlus, network):
    bicycle_speed_scanner = bikeTrainer(antPlus, network,
             {'onDevicePaired' : device_paired,
              'onSearchTimeout': search_timed_out,
              'onChannelClosed': channel_closed,
              'onBikeTrainer'  : bike_Trainer})
    # bicycle_speed_scanner.deviceType = 0x7b # Unsure if required.
    bicycle_speed_scanner.open()


#######################################
# Connect to the bicycle power sensor #
#######################################

#-------------------------------------------------#
#  ANT Callbacks for bicycle power sensor         #
#-------------------------------------------------#

def power_data(event_count, pedal_power_ratio, cadence, accumulated_power, instantaneous_power):
    print(f'Cadence: {cadence}, Power: {instantaneous_power}, accumulated: {accumulated_power}, ratio: {pedal_power_ratio}')
    powerAverage.add(instantaneous_power)

def torque_and_pedal_data(event_count, left_torque, right_torque, left_pedal_smoothness, right_pedal_smoothness):
    print(f'Torque: {left_torque} (left), {right_torque} (right),  pedal smoothness: {left_pedal_smoothness} (left), {right_pedal_smoothness} (right)')

#-------------------------------------------------#
#  Function for connecting bicycle power sensor   #
#-------------------------------------------------#

async def bicycle_power_connect(antPlus, network):
    bicycle_power_scanner = BicyclePower(antPlus, network,
                         {'onDevicePaired': device_paired,
                          'onSearchTimeout': search_timed_out,
                          'onChannelClosed': channel_closed,
                          'onPowerData': power_data,
                          'onTorqueAndPedalData': torque_and_pedal_data})
    bicycle_power_scanner.open()
    

####################################
# Connect to the heart rate sensor #
####################################

#-------------------------------------------------#
#  ANT Callbacks for heart rate sensor            #
#-------------------------------------------------#

def heart_rate_data(computed_heartrate, event_time_ms, rr_interval_ms):
    print(f'Heart rate: {computed_heartrate}, event time(ms): {event_time_ms}, rr interval (ms): {rr_interval_ms}')

#-------------------------------------------------#
#  Function for connecting heart rate sensor      #
#-------------------------------------------------#

async def heart_rate_connect(antPlus, network):
    heart_rate_scanner = HeartRate(antPlus, network,
                         {'onDevicePaired': device_paired,
                          'onSearchTimeout': search_timed_out,
                          'onChannelClosed': channel_closed,
                          'onHeartRateData': heart_rate_data})
    heart_rate_scanner.open()


#################
# Main Function #
#################

async def main():
    global powerAverage

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
    antPlus, network = await antplus_connect()

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

    await bicycle_speed_connect(antPlus, network)
    await bicycle_power_connect(antPlus, network)
    await heart_rate_connect(antPlus, network)

    while True:
        await asyncio.sleep(1 / rate)

        if isRecording:
            power = round(powerAverage.average(), 2)
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
            mqttClient.publish(topic= data_topic, payload= data)
            logger.info(f"{data_topic} -> {data}")

if __name__ == "__main__":
    asyncio.run(main())