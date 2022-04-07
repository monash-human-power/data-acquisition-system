const mqtt = require('mqtt');
const { ArgumentParser } = require('argparse');
const Ant = require('ant-plus');
const winston = require('./config/winston');
const RollingAverage = require('./utils/average');

// Required to detect speed sensor.
// The GitHub code has a SpeedScanner class which isn't accessible here for some reason.
// It uses a deviceType of 0x7b (SpeedCadenceScanner uses 0x79), and replacing it seems to work.
Ant.SpeedCadenceScanner.deviceType = 0x7b;

const argumentParser = new ArgumentParser({
  version: '1.0.0',
  addHelp: true,
  description: 'Ant-Plus MQTT Logger',
});

argumentParser.addArgument(['-i', '--id'], {
  help: 'Wireless sensor module ID',
  defaultValue: 4,
  type: 'int',
  action: 'store',
});

argumentParser.addArgument(['-a', '--host'], {
  help:
    'Address of the MQTT broker. If nothing is selected it will default to http://localhost.',
  defaultValue: 'http://localhost',
  action: 'store',
});

argumentParser.addArgument(['-r', '--rate'], {
  help: 'Rate to publish data in Hz',
  defaultValue: 1,
  type: 'float',
  action: 'store',
});

const args = argumentParser.parseArgs();
const { id: moduleID, host: mqttAddress, rate } = args;
winston.info(`Wireless module ID: ${moduleID}`);

const startTopic = `/v3/wireless_module/${moduleID}/start`;
const stopTopic = `/v3/wireless_module/${moduleID}/stop`;
const dataTopic = `/v3/wireless_module/${moduleID}/data`;
const statusTopic = `/v3/wireless_module/${moduleID}/status`;

// 700c 23mm tyre: https://www.bikecalc.com/wheel_size_math
const wheelCircumference = 2.09858; // m

/**
 * Connect to the MQTT broker
 *
 * @returns {Promise<mqtt.MqttClient>} Promise of MQTT client
 */
async function mqttConnect() {
  return new Promise((resolve) => {
    winston.info('Connecting to MQTT broker...');
    // Set the will for the mqtt connection so that we send an offline
    // status message upon disconnecting from the broker.
    const willPayload = { online: false };
    const will = {
      topic: statusTopic,
      payload: JSON.stringify(willPayload),
      retain: true,
    };

    const mqttOptions = {
      reconnectPeriod: 1000,
      connectTimeout: 5000,
      will,
    };

    const mqttClient = mqtt.connect(mqttAddress, mqttOptions);
    mqttClient.on('connect', () => {
      winston.info('Connected to MQTT broker');
      resolve(mqttClient);
    });
  });
}

/**
 * @typedef {import('ant-plus/build/ant').GarminStick3} GarminStick3
 */

/**
 * Connect to the ANT+ stick
 *
 * @returns {Promise<GarminStick3>} Promise of ANT+ stick instance
 */
async function antplusConnect() {
  return new Promise((resolve) => {
    const antPlus = new Ant.GarminStick3();
    winston.info('Finding ant-plus USB...');
    antPlus.openAsync(() => {
      antPlus.on('startup', () => {
        winston.info('ant-plus stick initialized');
        resolve(antPlus);
      });
    });
  });
}

/**
 * Connect to the bicycle speed sensor
 *
 * @param {GarminStick3} antPlus ANT+ stick instance
 */
async function bicycleSpeedConnect(antPlus) {
  return new Promise((resolve) => {
    const bicycleSpeedScanner = new Ant.SpeedCadenceScanner(antPlus);
    bicycleSpeedScanner.setWheelCircumference(wheelCircumference);
    bicycleSpeedScanner.scan();
    bicycleSpeedScanner.on('attached', () => {
      winston.info('Speed sensor attached');
      resolve(bicycleSpeedScanner);
    });
  });
}

/**
 * Connect to the bicycle power sensor
 *
 * @param {GarminStick3} antPlus ANT+ stick instance
 */
async function bicyclePowerConnect(antPlus) {
  return new Promise((resolve) => {
    const bicyclePowerScanner = new Ant.BicyclePowerScanner(antPlus);
    bicyclePowerScanner.scan();
    bicyclePowerScanner.on('attached', () => {
      winston.info('Bicycle power sensor attached');
      resolve(bicyclePowerScanner);
    });
  });
}

/**
 * Connect to the heart rate sensor
 *
 * @param {GarminStick3} antPlus ANT+ stick instance
 */
async function heartRateConnect(antPlus) {
  return new Promise((resolve) => {
    const heartRateScanner = new Ant.HeartRateScanner(antPlus);
    heartRateScanner.scan();
    heartRateScanner.on('attached', () => {
      winston.info('Heart rate sensor attached');
      resolve(heartRateScanner);
    });
  });
}

(async () => {
  let isRecording = false;
  let speed = 0;
  const powerAverage = new RollingAverage(3000);
  let cadence = 0;
  let heartRate = 0;
  const onlineMsg = { online: true };

  const mqttClient = await mqttConnect();
  const antPlus = await antplusConnect();

  // Announce we're online once ANT+ stick is also connected
  mqttClient.publish(statusTopic, JSON.stringify(onlineMsg), { retain: true });

  mqttClient.subscribe([startTopic, stopTopic]);
  mqttClient.on('message', (topic) => {
    winston.info(`Topic fired: ${topic}`);
    switch (topic) {
      case startTopic:
        isRecording = true;
        winston.info('Start publishing data');
        break;
      case stopTopic:
        isRecording = false;
        winston.info('Stop publishing data');
        break;
      default:
        winston.error(`Unexpected topic: ${topic}`);
        break;
    }
  });

  const bicycleSpeedScanner = await bicycleSpeedConnect(antPlus);
  bicycleSpeedScanner.on('speedData', (data) => {
    // Store speed into global variable
    const kmphToMps = 1 / 3.6;
    speed = data.speed * kmphToMps;
    winston.info(`ID: ${data.DeviceID}, Speed: ${speed}`);
  });

  const bicyclePowerScanner = await bicyclePowerConnect(antPlus);
  bicyclePowerScanner.on('powerData', (data) => {
    // Store power meter into global variable
    cadence = data.Cadence;
    const power = data.Power;
    powerAverage.add(power);
    winston.info(`ID: ${data.DeviceID}, Cadence: ${cadence}, Power: ${power}`);
  });

  const heartRateScanner = await heartRateConnect(antPlus);
  heartRateScanner.on('hbData', (data) => {
    // Store heart rate into global variable
    heartRate = data.ComputedHeartRate;
    winston.info(`ID: ${data.DeviceID}, Heart Rate: ${heartRate}`);
  });

  setInterval(() => {
    if (isRecording) {
      const power = Math.round(powerAverage.average() * 100) / 100;
      const payload = {
        sensors: [
          ...(speed ? [{ type: 'antPlusSpeed', value: speed }] : []),
          ...(power ? [{ type: 'power', value: power }] : []),
          ...(cadence ? [{ type: 'cadence', value: cadence }] : []),
          ...(heartRate ? [{ type: 'heartRate', value: heartRate }] : []),
        ],
      };
      const data = JSON.stringify(payload);
      mqttClient.publish(dataTopic, data);
      winston.info(`${dataTopic} -> ${data}`);
    }
  }, 1000 / rate);
})();
