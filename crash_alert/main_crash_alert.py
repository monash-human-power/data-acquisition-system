from dotenv import load_dotenv
from paho.mqtt import client as mqtt #import the client
from crash_alert import CrashAlert
import argparse
import logging
import os
import json

class CrashAlertDriver():
    """
    Class that runs the crash alert. Listens to messages from the crash detection.
    """
    def __init__(self, host, topic, cooldown, slack_webhook, port=1883):
        """
        Constructor for the class.

        :param host: a string representing the MQTT host
        :param topic: a string representing the MQTT topic to subscribe to
        :param cooldown: an integer representing the cooldown time in seconds for the crash alert
        :param slack_webhook: a string representing the webhook url for the slack api
        :param port: an optional integer representing the MQTT port, default to 1883
        """
        self.host = host
        self.port = port
        self.topic = topic
        self.client = None
        self.crash_alert = CrashAlert(cooldown, slack_webhook)
        self.true_count = 0

    @staticmethod
    def get_args(argv=None):
        """
        Get arguments passed into Python script.

        :param argv: an optional list of strings to manually input, by default None
        :returns: a dictionary containing all arguments passed from command line
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("--host", type=str, default="localhost", help="ip address")
        parsed_args = parser.parse_args(argv)
        return parsed_args

    def on_connect(self, client, userdata, flags, connection_result):
        """
        """
        self.client.subscribe(self.topic)

    def on_message(self, client, userdata, message):
        """
        """
        decoded_message = str(message.payload.decode("utf-8"))
        payload = json.loads(decoded_message)
        logging.info(f"MQTT message received: {payload}")
        if payload["value"]:
        #     self.true_count += 1
        # if self.true_count == 5:
            return_msg = self.crash_alert.alert()
            logging.debug(return_msg) 
            # self.true_count = 0

    def start(self):
        """
        """
        self.client = mqtt.Client()
        self.client.enable_logger()
        self.client.on_connect = self.on_connect 
        self.client.on_message = self.on_message 
        self.client.connect_async(self.host, self.port)
        self.client.loop_forever(retry_first_connection = True)


if __name__ == "__main__":
    load_dotenv()

    logging.basicConfig(
        format="%(levelname)-8s [%(filename)s] %(message)s", level=logging.DEBUG
    )

    slack_webhook = os.getenv("SLACK_WEBHOOK")
    ARGS = CrashAlertDriver.get_args()
    host = ARGS.host #os.getenv("MQTT_HOST") or 
    topic = "/v3/wireless_module/3/crash_detection"
    cooldown = 10

    CRASH_ALERT = CrashAlertDriver(host, topic, cooldown, slack_webhook)
    CRASH_ALERT.start()