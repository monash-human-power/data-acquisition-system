from slack_message_sender import SlackMessageSender
from sns_message_sender import SnsMessageSender
import time

class CrashAlert():
    def __init__(self, t):
        """
        """
        self.last_received_time = 0.0
        self.cooldown_time = t
        self.apis = [SlackMessageSender()]

    def alert(self):
        """
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