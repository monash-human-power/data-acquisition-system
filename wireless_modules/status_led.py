import machine
import uasyncio as asyncio


class LedState:
    def __init__(self, r, g, b, blink):
        self.r = r
        self.g = g
        self.b = b
        self.blink = blink


class WmState:
    Undefined = LedState(1, 1, 1, True)

    ConnectingToNetwork = LedState(1, 1, 0, False)
    InitialisingSensors = LedState(1, 1, 0, True)
    ConnectingToMqtt = LedState(0, 0, 1, True)
    Idle = LedState(0, 0, 1, False)
    Publishing = LedState(0, 1, 0, False)

    LowBattery = LedState(1, 0, 0, True)
    Error = LedState(1, 0, 0, False)


class StatusLed:
    def __init__(self, led_pins):
        self.r_pin = machine.Pin(led_pins[0], machine.Pin.OUT)
        self.g_pin = machine.Pin(led_pins[1], machine.Pin.OUT)
        self.b_pin = machine.Pin(led_pins[2], machine.Pin.OUT)

        self.state = None
        self.set_state(WmState.Undefined)

    def __set_leds_on(self):
        self.r_pin.on() if self.state.r else self.r_pin.off()
        self.g_pin.on() if self.state.g else self.g_pin.off()
        self.b_pin.on() if self.state.b else self.b_pin.off()

    def __set_leds_off(self):
        self.r_pin.off()
        self.g_pin.off()
        self.b_pin.off()

    def set_state(self, state):
        # Turn LEDs on instantly regardless of `start_blink_loop` so that if
        # the calling code is blocking, the color still changes
        if state is not self.state:
            self.state = state
            self.__set_leds_on()

    async def start_blink_loop(self):
        while True:
            self.__set_leds_on()
            await asyncio.sleep_ms(200)

            if self.state.blink:
                self.__set_leds_off()
                await asyncio.sleep_ms(200)
