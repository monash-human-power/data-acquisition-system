import serial
import time
import requests

ser = serial.Serial(
	'/dev/serial0',
	baudrate=500000,
	bytesize=serial.EIGHTBITS
	)

# Will create a filename of the format: data_YYYY_MM_DD_HH_MM_SS
def create_file_name():
	current_date_time = time.strftime('%Y_%m_%d_%H_%M_%S')
	output_filename = 'data_' + current_date_time
	return output_filename
	
DAS_server_address = "http://127.0.0.1:5000"

# Query server until it is online
# This will let Teensy know that the web server/Raspberry Pi is ready
is_server_online = False
while not is_server_online:
	try:
		print("Finding server")
		server_status = requests.get(DAS_server_address + '/server/status')
		is_server_online = server_status.json()["status"]
	# If server is not online
	except requests.exceptions.RequestException as error:
		continue

print("Connected to server")
is_recording = False
filename = ""

# Main loop
while True:
	# Actually tell Teensy that server is ready continuously until button is pressed 
	if not is_recording:
		output_message = "reading"
		ser.write(output_message.encode('utf-8'))
		time.sleep(0.1)

	# Check if there is anything in the input serial port
	serial_in_waiting = ser.in_waiting
	if serial_in_waiting > 0:
		# Read the contents of the input serial port
		serial_output = ser.readline() # Try ser.readline() ??
		output = str(serial_output.decode('utf-8')).rstrip()

		# Tell server to create a new csv file due to start of recording data
		if output == 'start':
			filename = create_file_name()
			start_body = {'filename' : filename}

			# TODO: Catch exceptions for the line below
			requests.post(DAS_server_address + '/start', data=start_body)
			is_recording = True
		elif output == 'stop':
			is_recording = False

		# Check if the button has been pressed  WHOLE data has been transmitted to the RPi properly
		if is_recording:
			# Specify which file to write to
			output += "&filename=" + filename
			body_headers = {'Content-Type' : 'application/x-www-form-urlencoded'}
			# TODO: Catch exceptions for the line below
			requests.request('POST', DAS_server_address + '/result', data=output, headers=body_headers)
		
		print(output)

	# Introduce some sort of delay so that the buffer can be cleared in time
	time.sleep(0.01)
