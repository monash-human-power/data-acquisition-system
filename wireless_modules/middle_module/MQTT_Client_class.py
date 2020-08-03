# Author: Kunj (most is also borrowed from mqtt_test written by Blake)
# Last modified: 3/08/2020
# Note: Can remove all the Print statements once all testing is successful

# Use micro pip to install packages
import utime
import upip
upip.install("micropython-umqtt.simple2")
try:
    from umqtt.simple import MQTTClient
except FileNotFoundError:
    print("Error in importing library")


class Client:
    def __init__(self, client_id, mqtt_broker):
        """
        Initialises the MQTT Client
        :param client_id: The unique client id used to initiate an MQTTClient class
        :param mqtt_broker: A string holding domain name or IP address of the broker to connect to, to send and receive
                            data.
        """
        self.client = MQTTClient(client_id, mqtt_broker)
        self.mqtt_broker = mqtt_broker

    def connect_and_subscribe(self, topics_to_subscribe, callback_func):
        """
        Connects to the MQTT broker and subscribes to topic in 'topics_to_subscribe'
        :param topics_to_subscribe: An array of topics to subscribe to.
                                    Eah element must be a string or byte literal (the latter is preferred)
        :param callback_func: The function to be called whenever a message from the subscribed topics is received.
        :return: True if a connection to the Broker is successfully established, otherwise False
        """

        # Provide the function to run whenever a message is received from the subscribed topics
        self.client.set_callback(callback_func)
        try:
            # Connect to MQTT broker
            self.client.connect()
            print('Connected to %s MQTT broker' % (self.mqtt_broker))
        except OSError:
            return False

        # Subscribe to each topic
        for topic in topics_to_subscribe:
            self.client.subscribe(topic)
            print('Subscribed to %s topic' % (topic))

        return True

    def _to_bytes_literal(self, data):
        """
        Converts 'data' into a form MQTT can read
        :param data: A string of data to convert to bytes literal
        :return: The bytes literal version of the 'data'
        """
        str_data = str(data)
        return str.encode(str_data)

    def mqtt_pub(self, data, topic):
        """
        This functions takes care of all of the formatting and publishes 'data' on the given 'topic'. It also checks for
        any pending message, but this should not be relied upon solely - use the check_for_message() method externally
        when an incoming message is to be checked for/read.
        :param data: A string of data to be sent
        :param topic: A string representing the topic to send 'data' to.
        :return: Nothing
        """
        try:
            # convert the data to bytes literal so that MQTT can read it
            msg = self._to_bytes_literal(data)

            # Publish the data on the given topic
            self.client.publish(topic, msg)

            # Check for any pending messages on any of the subscribed topics
            self.check_for_message()

            # print("MQTT data sent: %s on %s through %s" % (msg, topic, self.mqtt_broker))

        except OSError:
            print("OSError, check line 80 of MQTT_Client_class.py")
            # restart_and_reconnect()

    def check_for_message(self):
        """
        Checks whether an incoming message from the MQTT broker on the subscribed topics is pending. This check is done
        within the mqtt_pub method as well, but it gives a way to check manually for any
        message (especially given that the MQTT Client is only held by this class).
        :return: None
        """
        # If there's a message waiting, it will be sent to the callback_func defined in the connect_and_subscribe method
        self.client.check_msg()

    def wait_for_message(self):
        """
        Waits for a message from one of teh subscribed topics. Note: This function will only finish executing when
        a message is received and dealt in the set callback_func.
        :return: None
        """
        # Keep checking for any incoming message/s until one is read
        self.client.wait_msg()
