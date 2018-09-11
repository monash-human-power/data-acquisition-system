const path = require('path');
var winston = require("../node_modules/winston");

var options = {
    file: {
        level: "info",
        filename: path.join(__dirname, "../logs/DAS.log"),
        handleExceptions: true,
        json: true,
        maxsize: 5242880, // 5MB
        maxFiles: 5,
    },
    console: {
        format: winston.format.combine(
            winston.format.colorize({level: true}),
            winston.format.simple()
          ),
        level: "debug",
        handleExceptions: true,
        json: false,
    },
}

var logger = winston.createLogger({
    transports: [
      new winston.transports.File(options.file),
      new winston.transports.Console(options.console)
    ],
    exitOnError: false,
  });

 module.exports = logger;