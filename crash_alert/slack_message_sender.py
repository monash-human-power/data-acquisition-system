from message_sender_base import MessageSender
import requests

class SlackMessageSender(MessageSender):
    def __init__(self):
        """
        Initialises a message sending object for Slack.
        """
        self.name = "Slack"
        self.webhook = 'https://hooks.slack.com/services/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'

        # test message
        # self.send_test_message()

    def send_message(self, message):
        payload = '{"text": "%s"}' % f"<!channel> {message} :mega:"
        response = requests.post(
            self.webhook,
            data = payload
        )
        # print(response.text)