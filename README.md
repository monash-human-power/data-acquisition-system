T2 VCU Data Acquisition System
This repository contains the Raspberry Pi Vehicle Control Unit (VCU) software used by Monash Human Power T2.
The VCU currently performs two main tasks:
Reads vehicle sensor data.
Streams camera footage and telemetry to the rider phone.
The camera and telemetry pipelines are intentionally kept separate. SPI support has been added as an independent hardware communication layer; no SPI sensor is registered yet.
---
Current System Architecture
```text

                         Raspberry Pi 5 VCU

                                |

              +-----------------+-----------------+

              |                                   |

              |                                   |

         Camera Pipeline                   Telemetry Pipeline

              |                                   |

         Camera.cpp                        VCUController

              |                                   |

         rpicam-vid                         SensorManager

              |                                   |

           FFmpeg                              Sensors

              |                                   |

          MediaMTX                         SensorReading

              |                                   |

            RTSP                           DataSerialiser

              |                                   |

              |                           CommunicationManager

              |                                   |

              +---------------+-------------------+

                              |

                         Ethernet link

                              |

                        Android Phone

```
The Raspberry Pi uses the fixed Ethernet address:
```text

10.55.0.1

```
The Android phone currently uses:
```text

10.55.0.2

```
---
Program Startup
The program begins in:
```text

src/main.cpp

```
`main.cpp` is responsible for starting the camera system and starting the main VCU controller.
The basic startup flow is:
```text

main()

 |

 +--> Register SIGINT handler

 |

 +--> Create Camera

 |

 +--> Camera::startStream()

 |

 +--> Create VCUController

 |

 +--> VCUController::run()

```
The camera and sensor systems then run alongside each other.
Pressing:
```text

Ctrl+C

```
stops the camera stream before the VCU exits.
---
Camera Pipeline
The camera system is intentionally separate from the sensor telemetry system.
The current pipeline is:
```text

Pi Camera

   |

   v

Camera.cpp

   |

   v

rpicam-vid

   |

   v

FFmpeg

   |

   v

MediaMTX

   |

   v

RTSP

   |

   v

Android Phone

```
The current camera stream is available at:
```text

rtsp://10.55.0.1:8554/cam1

```
The camera implementation is contained in:
```text

src/sensors/Camera.h

src/sensors/Camera.cpp

```
Changes to telemetry should not require changes to the camera pipeline.
---
VCU Controller
The main VCU logic is handled by:
```text

src/core/VCUController.h

src/core/VCUController.cpp

```
When `VCUController::run()` starts, it first calls:
```cpp

setup();

```
The setup process currently:
```text

Initialise CommunicationManager

        |

        v

Create I2C bus

/dev/i2c-1

        |

        v

Create GyroscopeSensor

        |

        v

Add sensor to SensorManager

        |

        v

Initialise sensors

        |

        v

Calibrate gyroscope

        |

        v

Start main VCU loop

```
---
Main Sensor Loop
Once setup has completed, the VCU continuously performs:
```text

SensorManager::readAll()

        |

        v

SensorManager::getReadings()

        |

        v

vector<SensorReading>

        |

        v

DataSerialiser::toJSON()

        |

        v

vector<string>

        |

        v

CommunicationManager::sendMessages()

        |

        v

Phone

```
The loop then sleeps according to:
```cpp

config.getSensorReadIntervalMs()

```
before reading the sensors again.
The high-level loop is:
```cpp

while (running)

{

    sensorManager.readAll();

    std::vector<SensorReading> readings =

        sensorManager.getReadings();

    std::vector<std::string> messages =

        DataSerialiser::toJSON(readings);

    communicationManager.sendMessages(messages);

    // Wait until next sensor sample

}

```
---
Sensors
All sensors inherit from:
```text

SensorBase

```
defined in:
```text

src/sensors/Sensor.h

```
A sensor is responsible for:
```text

Initialising hardware

Reading hardware

Updating its SensorReading

```
A sensor should NOT be responsible for:
```text

JSON formatting

TCP networking

Phone communication

```
Those responsibilities belong to `DataSerialiser` and `CommunicationManager`.
---
SensorReading
Sensor data is passed through the system using:
```text

src/data/SensorReading.h

```
The current generic structure is:
```cpp

struct SensorReading

{

    std::string sensorID;

    std::uint64_t timestamp;

    std::unordered_map<std::string, float> values;

    bool isValid;

};

```
The `values` map allows different sensors to provide different measurements without changing the common VCU architecture.
For example, the gyroscope currently produces:
```text

accel_x

accel_y

accel_z

gyro_x

gyro_y

gyro_z

temperature_c

```
A future wheel-speed sensor could simply provide:
```text

speed_kmh

```
without requiring a different `SensorReading` structure.
---
Gyroscope
The currently implemented sensor is an MPU6050.
Files:
```text

src/sensors/GyroscopeSensor.h

src/sensors/GyroscopeSensor.cpp

```
It is currently connected directly to:
```text

/dev/i2c-1

```
with I2C address:
```text

0x68

```
The sensor reads:
```text

Accelerometer X

Accelerometer Y

Accelerometer Z

Gyroscope X

Gyroscope Y

Gyroscope Z

Temperature

```
During VCU startup, the gyroscope is calibrated.
The bike/gyro should remain still while the following message is displayed:
```text

Keep gyroscope still for calibration...

```
---
SensorManager
Files:
```text

src/core/SensorManager.h

src/core/SensorManager.cpp

```
`SensorManager` owns the collection of sensors.
Its main responsibilities are:
```text

addSensor()

initAll()

readAll()

getReadings()

getSensorCount()

```
`readAll()` asks every registered sensor to update its latest reading.
`getReadings()` then collects the latest `SensorReading` from every sensor.
This means additional sensors should generally only need to:
Implement the `SensorBase` interface.
Be added to `SensorManager` during VCU setup.
---
DataSerialiser
Files:
```text

src/data/DataSerialiser.h

src/data/DataSerialiser.cpp

```
`DataSerialiser` is responsible for converting `SensorReading` objects into JSON.
Sensors should not manually create JSON.
Example gyroscope packet:
```json

{

  "sensor": "gyro_1",

  "timestamp": 1791119904187,

  "values": {

    "temperature_c": 18.2506,

    "gyro_z": -0.106794,

    "gyro_y": 0.194046,

    "accel_z": 0.506104,

    "gyro_x": -0.0588548,

    "accel_y": 0.377686,

    "accel_x": -0.753418

  },

  "valid": true

}

```
The order of entries inside `values` should not be relied upon.
JSON object field order is not significant.
---
CommunicationManager
Files:
```text

src/communication/CommunicationManager.h

src/communication/CommunicationManager.cpp

```
`CommunicationManager` handles communication between the VCU and phone.
The current telemetry system runs a TCP server on:
```text

10.55.0.1:9001

```
The phone acts as the TCP client.
The data path is:
```text

VCU

 |

 | JSON over TCP

 v

10.55.0.1:9001

 |

 | Ethernet

 v

Android Phone

```
Each telemetry message is sent as JSON.
The telemetry connection is separate from the RTSP camera connection.
Therefore the phone receives:
```text

Camera:

rtsp://10.55.0.1:8554/cam1

Telemetry:

TCP 10.55.0.1:9001

```
---
Testing Telemetry Locally
Start the VCU:
```bash

./vcu

```
The output should include:
```text

Telemetry server ready on port 9001

Phone should connect to 10.55.0.1:9001

```
In another terminal on the Pi, connect using netcat:
```bash

nc 127.0.0.1 9001

```
You should receive JSON packets such as:
```json

{"sensor":"gyro_1","timestamp":1791119904187,"values":{"temperature_c":18.2506,"gyro_z":-0.106794,"gyro_y":0.194046,"accel_z":0.506104,"gyro_x":-0.0588548,"accel_y":0.377686,"accel_x":-0.753418},"valid":true}

```
Press:
```text

Ctrl+C

```
to exit netcat.
---
SPI Communication (New — Hardware Layer)
The VCU now includes a reusable SPI bus implementation in addition to the existing I2C bus. SPI support is not yet connected to `VCUController` or `SensorManager`, and no SPI sensor driver has been added.
Files
```text
src/hardware/SPIBus.h
src/hardware/SPIBus.cpp
tests/test_spi.cpp
```
`SPIBus` functionality
`openBus()` — opens a Linux `spidev` device and configures its SPI mode, bits per word and clock speed.
`closeBus()` — closes the file descriptor.
`transfer(tx, rx)` — performs a full-duplex SPI transfer: transmit and receive happen together.
`write(data)` — sends bytes while discarding received bytes.
`isOpen()` — reports whether the device is open.
The default constructor settings are:
```cpp
SPIBus spi("/dev/spidev0.0", 1000000, 0);
```
These specify device `/dev/spidev0.0`, a 1 MHz clock, and SPI mode 0. Settings may need changing for a particular sensor. The Linux SPI interface is accessed through `ioctl()` and `<linux/spi/spidev.h>`.
Compile SPI test
From the repository root, on Linux or WSL with the Linux SPI headers available:
```bash
g++ -std=c++17 tests/test_spi.cpp src/hardware/SPIBus.cpp -Isrc -o test_spi
```
Run the test on a Raspberry Pi with SPI enabled:
```bash
./test_spi
```
To check whether a Raspberry Pi exposes SPI devices:
```bash
ls /dev/spidev*
```
If needed, enable SPI under `sudo raspi-config` → Interface Options → SPI. Device names may vary with configuration.
Test status: The SPI code has been compiled with C++17 in WSL. A successful compile confirms source-level buildability, not successful communication with an SPI peripheral. WSL usually has no `/dev/spidev0.0`, and even a successful transfer on a Pi without a connected peripheral does not validate sensor data.
Future SPI sensor integration
When an SPI device is selected, implement a sensor-specific driver that reads the required registers and writes a `SensorReading`. Register it with `SensorManager` during `VCUController::setup()`. The existing `DataSerialiser` → `CommunicationManager` → phone telemetry path should remain unchanged. The camera pipeline is also unaffected.
---
Adding a New Sensor
When adding another sensor, preserve the current architecture:
```text

Hardware

   |

   v

Sensor subclass

   |

   v

SensorReading

   |

   v

SensorManager

   |

   v

DataSerialiser

   |

   v

CommunicationManager

   |

   v

Phone

```
A new sensor should:
Inherit from `SensorBase` or the appropriate sensor subclass.
Implement `init()`.
Implement `read()`.
Store measurements inside `lastReading.values`.
Set `lastReading.timestamp`.
Set `lastReading.isValid`.
Be registered with `SensorManager`.
Do not add networking code directly to a sensor.
Do not add JSON formatting directly to a sensor.
---
Source Structure
```text

src/

├── communication/

│   ├── CommunicationManager.cpp

│   └── CommunicationManager.h

│

├── config/

│   ├── SystemConfig.cpp

│   └── SystemConfig.h

│

├── core/

│   ├── SensorManager.cpp

│   ├── SensorManager.h

│   ├── VCUController.cpp

│   └── VCUController.h

│

├── data/

│   ├── DataSerialiser.cpp

│   ├── DataSerialiser.h

│   ├── SensorReading.cpp

│   └── SensorReading.h

│

├── hardware/

│   ├── I2CBus.cpp

│   ├── I2CBus.h
│   ├── SPIBus.cpp
│   └── SPIBus.h

│

├── sensors/

│   ├── Camera.cpp

│   ├── Camera.h

│   ├── GyroscopeSensor.cpp

│   ├── GyroscopeSensor.h

│   ├── I2CSensor.cpp

│   ├── I2CSensor.h

│   ├── Sensor.h

│   └── ...

│

└── main.cpp

```
---
Building the VCU
From the repository root:
```bash

g++ -std=c++17 src/main.cpp src/core/VCUController.cpp src/core/SensorManager.cpp src/config/SystemConfig.cpp src/communication/CommunicationManager.cpp src/data/DataSerialiser.cpp src/data/SensorReading.cpp src/hardware/I2CBus.cpp src/hardware/SPIBus.cpp src/sensors/I2CSensor.cpp src/sensors/GyroscopeSensor.cpp src/sensors/Camera.cpp -I. -Isrc -Isrc/core -Isrc/config -Isrc/communication -Isrc/data -Isrc/hardware -Isrc/sensors -Isrc/sensors/i2c -Isrc/sensors/analog -Isrc/util -pthread -o vcu

```
Run with:
```bash

./vcu

```
Stop with:
```text

Ctrl+C

```