# IMPORTS
import paho.mqtt.client as mqtt
from argparse import ArgumentParser
from config.winston import winston
import logging
from utils.average import RollingAverage

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
mqttAddress = args.host

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f'Wireless module ID: {module_id}')

v3StartTopic = 'v3/start';
dataTopic = f'/v3/wireless_module/${module_id}/data';
statusTopic = f'/v3/wireless_module/${module_id}/status';


# // 406c 28mm tyre: https://www.bikecalc.com/wheel_size_math
wheelCircumference = 1.44513 # m

# TODO
#
#