import serial 

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
		print(serial_output.decode('utf-8'))
