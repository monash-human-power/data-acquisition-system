from abc import abstractmethod

class MessageSender():
    """
    Abstract base class for all message senders.
    """
    def __init__(self):
        """
        Initialises the base message sender class. 
        """
    
    def send_test_message(self):
        """
        """
        self.send_message(f"This is a test message. If you receive this, {self.name} is ready for the crash alert.")

    @abstractmethod
    def send_message(self, message):
        """
        Performs the necessary method calls to send a message via the relevant api

        :param message: a string containing the message to be published to the message sending api
        """