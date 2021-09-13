import machine


class LedState:
    def __init__(self, r, g, b, blink):
        self.r = r
        self.g = g
        self.b = b
        self.blink = blink


class WmState:
    Undefined = LedState(1, 1, 1, True)
    LowBattery = LedState(1, 0, 0, True)
    ConnectingToNetwork = LedState(1, 1, 0, True)
    ConnectingToMqtt = LedState(1, 1, 0, False)
    InitialisingSensors = LedState(0, 0, 1, True)
    Idle = LedState(0, 0, 1, False)
    Publishing = LedState(0, 1, 0, False)


class StatusLed:
    def __init__(self, led_pins):
        self.r_pin = machine.Pin(led_pins[0], machine.Pin.OUT)
        self.g_pin = machine.Pin(led_pins[1], machine.Pin.OUT)
        self.b_pin = machine.Pin(led_pins[2], machine.Pin.OUT)

        self.state = None
        self.set_state(WmState.Undefined)

    def set_state(self, state):
        if state is not self.state:
            self.r_pin.on() if state.r else self.r_pin.off()
            self.g_pin.on() if state.g else self.g_pin.off()
            self.b_pin.on() if state.b else self.b_pin.off()
            self.state = state
