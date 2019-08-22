# Monash Human Power Data Acquisition System

This repository contains all the code related to Monash Human Power's Data Acquisition System (DAS).

# Getting Started
1. Type `git clone https://github.com/Monash-Human-Power/MHP_DAS.git` on the command line to download the whole repository.
2. Type `git submodule update --init` on the command line to download and update the submodules within the repository.

# Contents

## Raspi

### DAS.js
node.js program we run to communicate to the Teensy that is connected to the Raspberry Pi via serial communication.

## Teensy
| Script Name    | Description                                                                                                |
| -------------- | ---------------------------------------------------------------------------------------------------------- |
| DAS.ino        | Script that collects data from each sensor                                                                 |
| DAS_MOCK.ino   | Script that mocks fake data coming into the Teensy. Useful for checking if serial communication is working |
| DAS_NO_GPS.ino | DAS.ino with the GPS disabled. Useful for testing the DAS inside.                                          |
