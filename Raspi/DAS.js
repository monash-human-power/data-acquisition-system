let findAntPlusInterval;
let FILENAME = null;

/* Modules */
const path = require('path');

// Set up logging
const winston = require(path.join(__dirname, 'config/winston'));

/* Serial connection */
// Set up serial port connection
const SerialPort = require('serialport');

const serialportOptions = {
  autoOpen: false,
  baudRate: 500000,
  dataBits: 8,
  stopBits: 1,
  parity: 'none',
};
const serialPort = new SerialPort('/dev/serial0', serialportOptions, (err) => {
  // Print out error with opening serial port
  if (err) {
    winston.error(err);
  }
});
// Parse incoming data;
const Readline = SerialPort.parsers.Readline;
const parser = new Readline();
serialPort.pipe(parser);

/* ANT++ */
// Set up ant-plus dongle
const Ant = require('ant-plus');

const antPlus = new Ant.GarminStick3();
const bicyclePowerSensor = new Ant.BicyclePowerSensor(antPlus);

/* MQTT */
// Set up mqtt
const mqtt = require('mqtt');

const mqttOptions = {
  reconnectPeriod: 1000,
  connectTimeout: 5000,
};
const mqttClient = mqtt.connect('mqtt://localhost:1883', mqttOptions);

/* Start of main code */

function connectWithTeensy() {
  // Open event to tell us when connection with teensy has been made
  serialPort.open((err) => {
    if (err) {
      winston.error(err.message);
    } else {
      winston.info('Serial port open');
    }
  });

  serialPort.write('reading', (err) => {
    if (err) {
      winston.error('Error on write: ', err.message);
    } else {
      winston.info('Reading Teensy Data!');
    }
  })
}

// Check if ant-plus dongle is connected to Raspberry Pi
function checkAntPlusConnection() {
  if (!antPlus.open()) {
    winston.error('Ant-plus usb stick not found!');
    return false;
  }
  // Stop looking for ant-plus dongle
  clearInterval(findAntPlusInterval);
  setImmediate(connectWithTeensy);
  return true;
}

// Only ran if connected to mqtt broker
function mqttConnected() {
  findAntPlusInterval = setInterval(() => {
    winston.info('Finding ant-plus USB...');
    checkAntPlusConnection();
  }, 1000);
}

// Receive filename for us to use
let IS_RECORDING = false;
let INITIAL_TIME = 0;
function main(topic, message) {
  winston.info(`Topic fired: ${topic}`);
  switch (topic) {
    // Filename to use
    case 'filename':
      FILENAME = message.toString();
      IS_RECORDING = true;
      break;
    default:
      winston.error(`Unexpected topic: ${topic}`);
  }
}

winston.info('Connecting to mqtt server...');
mqttClient.subscribe('filename');
mqttClient.on('connect', mqttConnected);
mqttClient.on('message', main);

antPlus.on('startup', () => {
  winston.info('ant-plus stick initialized');
  // Connect to the first device found
  bicyclePowerSensor.attach(0, 0);
});

let CADENCE = 0;
let POWER = 0;
serialPort.on('open', () => {
  winston.info('Port opened with Teensy');
  // Power meter data
  bicyclePowerSensor.on('powerData', (data) => {
    if (IS_RECORDING) {
      // Store power meter into global variable
      CADENCE = data.Cadence;
      POWER = data.Power;
      winston.info(`ID: ${data.DeviceID}, Cadence: ${CADENCE}, Power: ${POWER}`);
    }
  });

  // mqtt broker and Teensy need to be both connected to receive data
  parser.on('data', (data) => {
    winston.info(`Teensy - ${data}`);
    if (data === 'start') {
      // Let mqtt broker know we have started recording
      mqttClient.publish('start');
      INITIAL_TIME = Math.floor(Date.now());
    } else if (data === 'stop') {
      // Reset variables
      IS_RECORDING = false;
      CADENCE = 0;
      POWER = 0;
    }

    if (IS_RECORDING) {
      const currentTime = Math.floor(Date.now());
      const outputData = `${data}&filename=${FILENAME}&time=${(currentTime - INITIAL_TIME)}&power=${POWER}&cadence=${CADENCE}`;
      mqttClient.publish('data', outputData);
    }
  });
});
