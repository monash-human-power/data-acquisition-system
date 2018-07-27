import serial
import time
import requests

ser = serial.Serial(
	'/dev/serial0',
	baudrate=500000,
	bytesize=serial.EIGHTBITS
	)

DAS_server_address = "192.168.0.200:5000"

while True:
	# Check if there is anything in the buffer
	serial_in_waiting = ser.in_waiting
	if serial_in_waiting > 0:
		# Read and print the contents of the buffer
		serial_output = ser.read(serial_in_waiting)
		output = str(serial_output.decode('utf-8'))

		# Tell server to create a new csv file due to start of recording data
		if (output == 'start'):
			current_date_time = time.strftime('%Y_%m_%d_%H_%M_%S')
			filename = 'data_' + current_date_time
			start_body = {'filename' : filename}
			requests.post(DAS_server_address + '/start', data=start_body)
			print(filename)
		# Check if the WHOLE data has been transmitted to the RPi properly
		elif (len(output) > 100):
			requests.post(DAS_server_address + '/result', data=output)
		print(output)

	# Introduce some sort of delay so that the buffer can be cleared in time
	time.sleep(0.01)