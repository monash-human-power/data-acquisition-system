/* Set up modules */
// Set up server connection
const request = require('request-promise-native');
const DAS_SERVER_ADDR = "http://127.0.0.1:5000";
var IS_SERVER_CONNECTED = false;

// Set up serial port connection
var SerialPort = require('serialport');
var serialport_options = {
	autoOpen: false,
	baudRate: 500000,
	dataBits: 8,
	stopBits: 1,
	parity: 'none'
}
var serialPort = new SerialPort('/dev/serial0', serialport_options, (err) => {
	// Print out error with opening serial port
	if (err) {
		console.log(err);
	}
});
// Parse incoming data;
var Readline = SerialPort.parsers.Readline;
var parser = new Readline();
serialPort.pipe(parser);

// Set up ant-plus dongle
var Ant = require('ant-plus');
var ant_plus = new Ant.GarminStick3();
var bicyclePowerSensor = new Ant.bicyclePowerSensor(ant_plus);

/* Start of main code */
// Check if server is connected
function check_if_server_online() {
	// Sends a GET request to the /server/status endpoint
	request.get(DAS_SERVER_ADDR + '/server/status', {timeout: 1000}, (error, res, body) => {
		if (error) {
			console.log(error);
			return false;
		}

		if (res.statusCode == 200) {
			// Stop asking server if online
			clearInterval(find_server_interval);
			// Run main code after function returns
			setImmediate(main);
			return true;
		} else {
			return false;
		}
	});
}

// Check if server is online every 1.5 seconds
const find_server_interval = setInterval(() => {
	console.log("Finding server");
	check_if_server_online()
}, 1500);

function main(){
	// Open event to tell us when connection with teensy has been made
	serialPort.open((err) => {
		if (err) {
			return console.error(err.message);
		}
		console.log('Serial port open');
	})
}

/*
	File name is created by asking the server what files are currently stored on the server.
	The file name will be of the format data_i where i will continue to increment

	This file name convention was created since the Raspberry Pi Zero W does not have an onboard RTC.
*/
function create_file_name() {
	let file_name_request_options = {
		method: 'GET',
		url: DAS_SERVER_ADDR + '/files',
		json: true
	}
	return request.get(file_name_request_options)
		.then((response) => {
			let files = response.files;
			if (files.length == 0) {
				return 'data_0';
			}

			var i = 0;
			do {
				var filename = 'data_' + i;
				i++;
			} while (files.includes(filename + '.csv'));
			return filename;
		})
		.catch((error) => {
			console.error("Error in asking server for list of files");
			return Promise.reject(error);
		})
}

var initial_time = 0;
var IS_RECORDING = false;
var current_filename = "";
serialPort.on("open", () => {
	console.log('Port opened with Teensy');
	
	// Server and Teensy need to be both connected to receive data
	parser.on('data', (data) => {
		console.log(data);
		if (data == 'start') {
			create_file_name()
				.then((created_filename) => {
					current_filename = created_filename;
					var start_body = {filename: current_filename};
					let create_file_name_post_options = {
						method: 'POST',
						url: DAS_SERVER_ADDR + '/start',
						body: start_body,
						json: true
					};
					// Save the time we send the first data point
					initial_time = Math.floor(Date.now());
					request(create_file_name_post_options, (error, response, body) => {
						if (error) {
							console.error(error);
						}
						// TODO: Tell Teensy that Raspberry Pi was unable to start a new file
					 })
					 .then(() => {
						IS_RECORDING = true;
					 })
				})
				.catch((error) => {
					console.error(error);
				})
		} else if (data == "stop") {
			IS_RECORDING = false;
		}

		if (IS_RECORDING) {
			let current_time = Math.floor(Date.now());
			data += "&filename=" + current_filename;
			data += "&time=" + (current_time - initial_time);
			let post_data_request_options = {
				method: 'POST',
				url: DAS_SERVER_ADDR + '/result',
				body: data,
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				}
			}
			request(post_data_request_options, (error, response, body) => {
				if (error) {
					console.error(error);
				}
			})
		}
	});
})