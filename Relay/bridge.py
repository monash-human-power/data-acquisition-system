import time
import sys
import argparse
import json
import paho.mqtt.client as mqtt
from zetarf433 import PyZetaRF433, Status
from protocol import RXProtocol, TXProtocol, PACKET_LENGTH

parser = argparse.ArgumentParser(
  description='MQTT to Zeta433 bridge.',
  add_help=True
)
parser.add_argument(
  '-c', '--channel', action='store', type=int, default=4,
  help='Zeta433 channel to communicate over. Defaults to 4.'
)
parser.add_argument(
  '--host', action='store', type=str, default="localhost",
  help="""Address of the MQTT broker. Defaults to localhost."""
)
args = parser.parse_args()
zeta_channel = args.channel
broker_address = args.host

rx = RXProtocol()
tx = TXProtocol()

def on_mqtt_connect(client, userdata, flags, rc):
  print('Connected to MQTT broker')
  mqtt_client.subscribe('#')

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_mqtt_connect
mqtt_client.connect(broker_address)
mqtt_client.loop_start()

zeta = PyZetaRF433(PACKET_LENGTH)
print('Starting Zeta TxRx...')
if not zeta.beginWithPacketLengthOf(PACKET_LENGTH):
  print('Zeta begin failed')
  sys.exit()

if not zeta.start_listening_on_channel(zeta_channel):
  print('Failed to begin listening')
  sys.exit()

send_queue = []

def on_zeta_message(message):
  (topic, payload) = json.loads(message)
  print(f'RX {msg.topic}')
  mqtt_client.publish(topic, payload)
rx.on_message = on_zeta_message

def on_mqtt_message(client, userdata, msg):
  global send_queue
  print(f'TX {msg.topic}')
  p = msg.payload.decode('utf-8')
  payload = json.dumps([msg.topic, p])
  send_queue += tx.pack(str(payload))
mqtt_client.on_message = on_mqtt_message

while True:
  if zeta.check_received():
    packet = zeta.read_packet(PACKET_LENGTH)
    rx.receive_packet(packet)
  if len(send_queue) > 0:
    packet = send_queue.pop(0)
    zeta.send_packet(zeta_channel, packet, PACKET_LENGTH)
    while not zeta.check_for(Status.DataTransmitted):
      pass