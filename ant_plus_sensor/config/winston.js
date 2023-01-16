const path = require('path');
const winston = require('../node_modules/winston');

const options = {
  file: {
    level: 'info',
    filename: path.join(__dirname, '../logs/ant_plus.log'),
    handleExceptions: true,
    json: true,
    maxsize: 5242880, // 5MB
    maxFiles: 5,
  },
  console: {
    format: winston.format.combine(
      winston.format.colorize({ level: true }),
      winston.format.simple(),
    ),
    level: 'debug',
    handleExceptions: true,
    json: false,
  },
};

const logger = winston.createLogger({
  transports: [
    new winston.transports.File(options.file),
    new winston.transports.Console(options.console),
  ],
  exitOnError: false,
});

module.exports = logger;
