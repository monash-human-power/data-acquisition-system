import pyfirmata
import time

board = pyfirmata.Arduino('/dev/ttyACM0')
pin13 = board.get_pin('d:13:o')

while True:
    time.sleep(1)
    print("on")
    pin13.write(1)
    time.sleep(1)
    print("off")
    pin13.write(0)
