from message_senders.message_sender_base import MessageSender
import requests

class SlackMessageSender(MessageSender):
    def __init__(self, webhook):
        """
        Initialises a message sending object for Slack.
        """
        self.name = "Slack"
        self.webhook = webhook

    def send_message(self, message):
        payload = '{"text": "%s"}' % f"<!channel> {message} :mega:"
        response = requests.post(
            self.webhook,
            data = payload
        )