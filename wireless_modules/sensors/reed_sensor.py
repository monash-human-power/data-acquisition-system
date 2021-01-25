import machine
import time

from sensor_base import Sensor

US_TO_S = 1e-6

# Ignore anything shorter than 50ms, likely to be switch bouncing.
# (roughly corresponds to 150 km/h)
MIN_REVOLUTION_TIME = 50_000  # us
# If a wheel revolution has taken longer than this duration,
# assume speed is zero. (roughly corresponds to 1.5 km/h)
MAX_REVOLUTION_TIME = 5_000_000  # us


class ReedSensor(Sensor):
    def __init__(self, reed_pin: int, tyre_circumference: float):
        self.tyre_circumference = tyre_circumference
        self.last_trigger_time = time.ticks_us()
        self.current_speed = 0
        self.distance_travelled = 0

        pin = machine.Pin(reed_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.reed_callback)

    def reed_callback(self, pin):
        now = time.ticks_us()
        diff_us = time.ticks_diff(now, self.last_trigger_time)

        if diff_us < MIN_REVOLUTION_TIME:
            return

        self.last_trigger_time = now
        self.distance_travelled += self.tyre_circumference
        self.current_speed = self.tyre_circumference / (diff_us * US_TO_S)

    def read(self):
        now = time.ticks_us()
        diff = time.ticks_diff(now, self.last_trigger_time)
        current_speed = self.current_speed if diff < MAX_REVOLUTION_TIME else 0

        return [
            {"type": "reedVelocity", "value": current_speed},
            {"type": "reedDistance", "value": self.distance_travelled},
        ]
