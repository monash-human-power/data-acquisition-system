import machine
import time

from sensor_base import Sensor

US_TO_S = 1e-6

# Ignore anything shorter than 50ms, likely to be switch bouncing.
# (roughly corresponds to 150 km/h)
MIN_REVOLUTION_TIME = 50_000  # microseconds
# If a wheel revolution has taken longer than this duration,
# assume speed is zero. (roughly corresponds to 1.5 km/h)
MAX_REVOLUTION_TIME = 5_000_000  # microseconds


class ReedSensor(Sensor):
    def __init__(self, reed_pin: machine.Pin, tyre_circumference: float):
        """
        Initialise the reed switch speed sensor.
        :param reed_pin: The pin that the reed switch is attached to.
        :param tyre_circumference: Circumference of the tyre the reed switch measures.
        """
        self.tyre_circumference = tyre_circumference
        self.last_trigger_time = time.ticks_us()
        self.current_speed = 0
        self.distance_travelled = 0

        # Configure reed_pin as an input pulled up internally, and set up reed_callback
        # to be called whenever pin is driven low.
        reed_pin.init(mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        reed_pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.reed_callback)

    def reed_callback(self, pin: machine.Pin):
        """
        Handle interrupt triggered when the reed_pin is driven low.
        Will update the speed and distance travelled if sufficient time has passed
        since the last interrupt.
        :param pin: The pin that triggered the interrupt. Unused.
        """
        now = time.ticks_us()
        diff_us = time.ticks_diff(now, self.last_trigger_time)

        # Ignore short intervals between triggers, this is likely the switch bouncing.
        if diff_us < MIN_REVOLUTION_TIME:
            return

        self.last_trigger_time = now
        self.distance_travelled += self.tyre_circumference
        self.current_speed = self.tyre_circumference / (diff_us * US_TO_S)

    def read(self):
        """
        Return the current speed and distance travelled of the bike.
        :return: An array containing the velocity data and the distance data as
            separate elements.
        """
        now = time.ticks_us()
        diff = time.ticks_diff(now, self.last_trigger_time)
        current_speed = self.current_speed if diff < MAX_REVOLUTION_TIME else 0

        return [
            {"type": "reedVelocity", "value": current_speed},
            {"type": "reedDistance", "value": self.distance_travelled},
        ]

    def on_start(self):
        """ Reset the speed and distance travelled by the bike. """
        # Disable IRQ temporarily to avoid race conditions
        irq_state = machine.disable_irq()
        self.last_trigger_time = time.ticks_us()
        self.current_speed = 0
        self.distance_travelled = 0
        machine.enable_irq(irq_state)
