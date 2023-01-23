from message_senders.slack_message_sender import SlackMessageSender
from message_senders.sns_message_sender import SnsMessageSender
import time

class CrashAlert():
    def __init__(self, min_time_interval, slack_webhook):
        """
        Class for sending the alerts when a crash happens.

        :param min_time_interval: the minimum cooldown time required between crash detections
        :param slack_webhook: the webhook for the Slack API
        """
        self.last_received_time = 0.0
        self.cooldown_time = min_time_interval
        self.apis = [SlackMessageSender(slack_webhook)]

    def alert(self):
        """
        Sends the alerts via the message sending apis.

        :returns: a string indicating the outcome of the alert
        """
        time_now = time.time()
        if time_now - self.last_received_time > self.cooldown_time:
            time_now_string = time.strftime("%H:%M:%S")
            for message_sender in self.apis:
                message_sender.send_message(f"The bike has crashed at {time_now_string}")
                self.last_received_time = time_now
            return "sent messages"
        else:
            return "time since last message sent is too short"