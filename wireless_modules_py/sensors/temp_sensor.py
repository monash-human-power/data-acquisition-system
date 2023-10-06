import pigpio
import time
pi=pigpio.pi()
def dht22(pin):
  global pi
  pi.setmode(pin,pigpio.INPUT)
  pi.set_pull_up_down(pin, pigpio.PUD_UP)
    data = []
    last_state = 1
    bits = []
    try:
        while True:
            current_state = pi.read(pin)
            bits.append(1 if current_state == 1 and last_state == 0 else 0)
            last_state = current_state
            if len(bits) == 40:
                break
       for i in range(0, len(bits), 8):
            byte = bits[i:i+8]
            data.append(int(''.join([str(bit) for bit in byte]), 2))
        humidity = data[0] + data[1]/float(10)
        temperature = (data[2] & 0x7f) + data[3]/float(10)
        if data[2] & 0x80:
            temperature *= -1
        return (humidity, temperature)
    except KeyboardInterrupt:
        pass
    finally:
        pi.cleanup()
