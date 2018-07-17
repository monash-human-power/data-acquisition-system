import serial
import time

ser = serial.Serial(
	'/dev/serial0',
	baudrate=500000,
	bytesize=serial.EIGHTBITS
	)

while True:
	# Check if there is anything in the buffer
	if ser.in_waiting > 0:
		# Read and print the contents of the buffer
		serial_output = ser.read(ser.in_waiting)
		output = serial_output.decode('utf-8')
		print(output)

	# Introduce some sort of delay so that the buffer can be cleared in time
	time.sleep(0.01)