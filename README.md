# Monash Human Power Data Acquisition System

This repository contains all the code related to Monash Human Power's Data Acquisition System (DAS).

# Getting Started
1. Type `git clone https://github.com/Monash-Human-Power/MHP_DAS.git` on the command line to download the whole repository.
2. Type `git submodule update --init` on the command line to download and update the submodules within the repository.

# Contents
## Packaging
Contains various Solidworks models that packages the DAS into a neat package.

## Raspi
### ant-plus-app
A node.js application that connects to a power meter using an ant+ dongle and outputs the cadence and power onto the command line.

### DAS.py
The python script that talks to the Teensy. When making changes to this file, DAS.py should **not** know anything about the internals of the web server. It should only know about the endpoints of the server. (Do not use file paths to the inside of the server within this script)

## Teensy
### DAS
Contains the sketch that we upload onto the Teensy that collects data from each sensor.