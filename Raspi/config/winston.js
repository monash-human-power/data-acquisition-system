const path = require('path');
var winston = require(path.join(__dirname, "../winston"));

var options = {
    file: {
        level: "info",
        filename: path.join(__dirname, "../logs/DAS.log"),
        handleExceptions: true,
        json: true,
        maxsize: 5242880, // 5MB
        maxFiles: 5,
        colorize: false,
    },
    console: {
        level: "debug",
        handleExceptions: true,
        json: false,
        colorize: true,
    },
}

var logger = new winston.Logger({
    transports: [
      new winston.transports.File(options.file),
      new winston.transports.Console(options.console)
    ],
    exitOnError: false,
  });
  
  logger.stream = {
    write: function(message, encoding) {
      logger.info(message);
    },
  };
  
  module.exports = logger;