# Raspberry Pi Files

## Getting Started
### Setting up Node.js libraries
To install the necessary libraries for node.js you may need to manually install them instead of running `npm install`.

#### Installing serialport
```
sudo npm install serialport --unsafe-perm --build-from-source 
```
Running without the flags will lead to errors. See [this](https://github.com/node-serialport/node-serialport/tree/master/packages/serialport#raspberry-pi-linux) for more information about this.