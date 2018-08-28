/* Set up modules */
// Set up server connection
const request = require('request');
const DAS_SERVER_ADDR = "http://127.0.0.1:5000";
var IS_SERVER_CONNECTED = false;

// Set up serial port connection
var serialport = require('serialport');
var serialport_options = {
	baudRate: 500000,
	dataBits: 8,
	stopBits: 1,
	parity: 'none'
}
var serialPort = new SerialPort('/dev/serial0', serialport_options, (err) => {
	// Print out error with opening serial port
	console.log(err);
});
// Parse incoming data;
var Readline = serialport.parsers.Readline;
var parser = new Readline();
serialPort.pipe(parser);

/* Start of main code */
// Check if server is connected
while (!IS_SERVER_CONNECTED) {
	console.log('Finding server');
	request.get(DAS_SERVER_ADDR + '/server/status')
		.on('response', (response) => {
			console.log(response);
		})
}

// Open event to tell us when connection with teensy has been made
serialPort.on("open", () => {
	console.log('Port opened with Teensy');
	
	// Server and Teensy need to be both connected to receive data
	if (IS_SERVER_CONNECTED){
		parser.on('data', (data) => {
			console.log(data);
		});
	}
})