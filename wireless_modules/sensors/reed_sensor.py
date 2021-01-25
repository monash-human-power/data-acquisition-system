import machine
import time

from sensor_base import Sensor


us_to_s = 1e-6


class ReedSensor(Sensor):
    def __init__(self, reed_pin: int, tyre_circumference: float):
        self.last_trigger_time = time.ticks_us()
        self.current_speed = 0
        self.tyre_circumference = tyre_circumference

        pin = machine.Pin(reed_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.reed_callback)

    def reed_callback(self, pin):
        now = time.ticks_us()
        diff_us = time.ticks_diff(now, self.last_trigger_time)

        # Ignore anything shorter than 50ms (roughly corresponds to 150 km/h)
        if diff_us < 50_000:
            return

        self.last_trigger_time = now
        self.current_speed = self.tyre_circumference / (diff_us * us_to_s)

    def read(self):
        return [{"type": "reedVelocity", "value": self.current_speed}]
