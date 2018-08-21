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

// Open event to tell us when connection with teensy has been made
serialPort.on("open", () => {
	console.log('Port opened with Teensy');
	
	serialPort.on('data', (data) => {
		console.log(data);
	})
})