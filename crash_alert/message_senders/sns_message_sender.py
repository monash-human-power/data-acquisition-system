from message_senders.message_sender_base import MessageSender
import json
import boto3
from botocore.exceptions import ClientError

class SnsMessageSender(MessageSender):
    def __init__(self):
        """
        Initialises a message sending object for AWS SNS.
        """
        self.name = "AWS SNS"
        self.sns_resource = boto3.resource('sns')

        all_topics = self.list_topics()
        for topic in all_topics:
            self.topic = topic

    def list_topics(self):
        """
        Lists topics for the current account.

        :return: An iterator that yields the topics.
        """
        try:
            topics_iter = self.sns_resource.topics.all()
        except ClientError:
            print("Couldn't get topics.")
            raise
        else:
            return topics_iter

    def publish_multi_message(self, topic, subject, default_message, sms_message, email_message):
        """
        Publishes a multi-format message to a topic. A multi-format message takes
        different forms based on the protocol of the subscriber. For example,
        an SMS subscriber might receive a short, text-only version of the message
        while an email subscriber could receive an HTML version of the message.

        :param topic: The topic to publish to.
        :param subject: The subject of the message.
        :param default_message: The default version of the message. This version is
                                sent to subscribers that have protocols that are not
                                otherwise specified in the structured message.
        :param sms_message: The version of the message sent to SMS subscribers.
        :param email_message: The version of the message sent to email subscribers.
        :return: The ID of the message.
        """
        try:
            message = {
                'default': default_message,
                'sms': sms_message,
                'email': email_message
            }
            response = topic.publish(
                Message=json.dumps(message), Subject=subject, MessageStructure='json')
            message_id = response['MessageId']
        except ClientError:
            print(f"Couldn't publish message to topic {topic.arn}.")
            raise
        else:
            return message_id

    def send_message(self, message):
        """
        """
        self.publish_multi_message(self.topic, "CRASH ALERT", message, message, message)