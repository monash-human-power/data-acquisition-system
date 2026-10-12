T2 VCU Data Acquisition System
This repository contains the Raspberry Pi Vehicle Control Unit (VCU) software used by Monash Human Power T2.
The VCU currently performs two main tasks:
Reads vehicle sensor data.
Streams camera footage and telemetry to the rider phone.
The camera and telemetry pipelines are intentionally kept separate. SPI support has been added as an independent hardware communication layer and is used by the ADS131M08 strain gauge sensor.
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
The VCU now includes a reusable SPI bus implementation in addition to the existing I2C bus. It is used by the ADS131M08 strain gauge sensor described below.
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
Adding SPI sensors
SPI sensors inherit from `SPISensor` (`src/sensors/SPISensor.h`), which holds a reference to a shared `SPIBus`. Implement a sensor-specific driver that writes a `SensorReading` and register it with `SensorManager` during `VCUController::setup()`. The existing `DataSerialiser` → `CommunicationManager` → phone telemetry path should remain unchanged. The camera pipeline is also unaffected.
`openBus()`, `transfer()` and `isOpen()` are virtual so that tests can replace the bus with a simulated device.
---
Strain Gauges (ADS131M08 over SPI)
Full Wheatstone bridge strain gauges are read through a TI ADS131M08 8-channel, 24-bit ADC.
Files
```text
src/hardware/ADS131M08.h
src/hardware/ADS131M08.cpp
src/hardware/GPIOInput.h
src/hardware/GPIOInput.cpp
src/sensors/SPISensor.h
src/sensors/SPISensor.cpp
src/sensors/analog/StrainGaugeSensor.h
src/sensors/analog/StrainGaugeSensor.cpp
tests/test_strain_gauge.cpp
```
`ADS131M08` is the chip driver: frame building, RESET/RREG/WREG/NULL commands, PGA gain, oversampling ratio, global chop and output CRC checking. `StrainGaugeSensor` turns bridge voltages into strain. `GPIOInput` watches the ADC's DRDY pin for falling edges using the Linux GPIO character device (`/dev/gpiochipN`), so no extra library is needed.
SPI settings
The ADS131M08 uses SPI mode 1 (CPOL = 0, CPHA = 1), not the `SPIBus` default of mode 0. `VCUController` opens `/dev/spidev0.0` at 1 MHz in mode 1 (see `SystemConfig`). Frames are 10 words of 24 bits (30 bytes): a response word, eight channel words and a CRC word.
Hardware requirements
CLKIN is driven by the on-board SiT1602BC-21-25E-4.096000G oscillator (4.096 MHz, 2.5 V). This frequency is set by `StrainGaugeADCSettings::clockHz`, so change it there if the oscillator changes. The output data rate is (CLKIN / 2) / OSR:
```text
OSR     Data rate at 4.096 MHz
1024    2000 SPS
2048    1000 SPS
4096     500 SPS   (default)
8192     250 SPS
16256    126 SPS
```
The datasheet specifies low-power mode (CLOCK PWR = 01) at a 4.096 MHz CLKIN, so that is the default (`StrainGaugeADCSettings::powerMode`). The crystal oscillator circuit is turned off (XTAL_DIS) because CLKIN is driven by the external oscillator. With the default 8 samples per reading, each `read()` takes about 16 ms. The SYNC/RESET pin must be held high. If CLKIN is missing, the ADC still answers commands but never produces data, and initialisation fails with `timed out waiting for ADS131M08 data (check CLKIN)`.
Voltage reference
AVDD and DVDD are both 3.3 V. The ADS131M08 has no AVSS pin: AGND (0 V) is its negative supply. REFIN is driven to 1.25 V by a 10k/10k divider (R9/R12) from the 2.5 V rail, so the driver sets EXTREF_EN (CLOCK bit 6) to use it as the reference. The ADC then uses 0.96 × REFIN = 1.2 V, which gives a full-scale range of ±1.2 V / gain. These are the defaults in `StrainGaugeADCSettings` (`externalReference`, `refinVolts`).
EXTREF_EN is defined in the CLOCK register description (datasheet Table 8-17), although the summary register map (Table 8-12) shows it as reserved. The driver therefore reads CLOCK back. If the bit did not set, it prints `warning: EXTREF_EN did not set, using the internal 1.2 V reference`. Readings are still correct in that case, but no longer ratiometric. The startup line says which reference is in use.
The bridges are excited from the same 2.5 V rail, so the measurement is ratiometric: a low or noisy rail scales the bridge output and the reference together, so the strain value is unaffected.
Wiring to the Pi (via the VCU HAT)
The strain gauge board's J3 connects to J8 on the VCU HAT, which sits on the Pi's GPIO header. The HAT passes SCLK, MOSI, MISO and the chip selects through an ISO7761 digital isolator. The cable must be wired pin 1 to pin 1.
```text
ADC board J3   HAT J8      Path on the HAT              Pi 5 header
1  3.3 V       1  3V3      HAT 3V3 rail                 -
2  GND         2  GND      GND                          GND
3  SCLK        3  ISO-SCLK ISO7761 OUTC <- INC          pin 23 (GPIO 11)
4  DIN         4  ISO-MOSI ISO7761 OUTD <- IND          pin 19 (GPIO 10)
5  DOUT        5  ISO-MISO ISO7761 INF  -> OUTF         pin 21 (GPIO 9)
6  CS          6  ISO-CE0  ISO7761 OUTB <- INB          pin 24 (GPIO 8, CE0) -> /dev/spidev0.0
7  DRDY        7  ISO-INT0 (not through the isolator)   pin 18 (GPIO 24)
8  GND         8  GND      GND                          GND
```
ISO-CE0 has a 10k pull-up (R20), so the ADC stays deselected while the Pi is booting. HAT connector J9 is the same but uses CE1 (`/dev/spidev0.1`) and INT1 on pin 22 (GPIO 25), for a second SPI board.
DRDY
The ADC pulls DRDY low when a new conversion is ready, and DRDY falls again for every conversion even if the last one was not read. The ADC also buffers two samples per channel, so after the gap between VCU loop iterations both are full and old (datasheet 8.5.1.9.1). Each `read()` therefore drops stale DRDY edges, reads two frames to empty the buffer, and then, for each sample, waits for a falling edge on GPIO 24 and reads one SPI frame. Reading straight after DRDY falls also avoids reading while a conversion completes, which the datasheet warns blocks the next DRDY pulse. The GPIO is found by its chip label (`pinctrl-rp1` on the Pi 5) rather than a fixed `/dev/gpiochipN` path, because the number differs between kernel versions. Both the label and the line are set in `SystemConfig`.
If the GPIO cannot be opened, the sensor prints `warning: DRDY pin unavailable, polling STATUS instead` and keeps working by polling the STATUS register over SPI. The user running `./vcu` must be in the `gpio` group (and the `spi` group for `/dev/spidev0.0`), which the default Pi OS user already is. To check the pin from the shell, run `gpioinfo | grep -A30 pinctrl-rp1` (from the `gpiod` package) and look for line 24.
The isolator adds a delay to each signal, and MISO pays it twice: the clock goes out through the isolator and the data comes back through it. This has no effect at the default 1 MHz SCLK, but keep it in mind before raising `spiSpeedHz` far.
SYNC/RESET is pulled up to 3.3 V on the board through R19.
Hardware checks against the datasheet (SBAS950B, `adc_datasheet.pdf`)
- CLKIN level (out of spec): CLKIN is a digital input with VIH = 0.8 × DVDD = 2.64 V at DVDD = 3.3 V. The SiT1602BC-21-25E oscillator runs from 2.5 V, so its high level is at most 2.5 V. It may work on the bench, but it is below the guaranteed threshold. Use the 3.3 V version (SiT1602BC-21-33E-4.096000G) or power the oscillator from 3.3 V if the part allows it.
- Input voltage range: at gains of 8 to 128, each input must stay between AGND − 1.3 V and AVDD − 1.8 V (1.5 V at AVDD = 3.3 V). A bridge excited at 2.5 V sits at about 1.25 V, which is within range. A bridge excited at 3.3 V (about 1.65 V) would not be.
- REFIN: 1.1 V to 1.3 V, nominal 1.25 V. The full-scale range keeps the 1.2 : 1.25 ratio, which is the 0.96 factor used in the code.
- CLKIN frequency: 0.3 to 4.15 MHz in low-power mode, so 4.096 MHz is within range.
- CAP 220 nF, AVDD and DVDD 1 µF: matches the strain gauge board.
Raspberry Pi 5 setup
Enable SPI with `sudo raspi-config` → Interface Options → SPI, or add `dtparam=spi=on` to `/boot/firmware/config.txt`, then reboot. Check that `/dev/spidev0.0` exists (`ls /dev/spidev*`). This is SPI0 with chip select CE0, which the HAT routes to J8. If the strain gauge board is moved to J9 (CE1), change `spiDevicePath` in `SystemConfig` to `/dev/spidev0.1`.
Channel configuration
Each bridge is described by a `StrainChannelConfig`:
```cpp
StrainChannelConfig bridge0;
bridge0.name = "strain_0";        // telemetry key prefix
bridge0.channel = 0;              // AIN0P / AIN0N
bridge0.gaugeFactor = 2.1f;       // value on the gauge packet (spec 2.0-2.2)
bridge0.bridgeFactor = 1.0f;      // 1.0 for 4 active gauges
bridge0.excitationVoltage = 2.5f; // bridge excitation (2.5 V rail)
bridge0.pgaGain = 32;             // input range +/- 1.2 V / gain
```
Strain is calculated as:
```text
strain = (Vout - Vout_at_tare) / Vex / (gaugeFactor * bridgeFactor)
```
Use `bridgeFactor = (1 + poisson) / 2` for a full bridge with two axial and two Poisson gauges. A negative `bridgeFactor` flips the sign if the bridge is wired the other way round.
Choose the PGA gain so the largest expected bridge output, plus any bridge imbalance, stays inside +/- 1.2 V / gain. For example, 1000 microstrain with GF 2.0 and 2.5 V excitation gives 5 mV, which fits at gain 64 (+/- 18.75 mV) or gain 128 (+/- 9.375 mV).
Up to eight bridges can be read by one sensor by passing several `StrainChannelConfig` entries.
Startup and readings
During `VCUController::setup()` the sensor resets the ADC, checks the ID register, configures it, and then tares. The structure must be unloaded while this message is displayed:
```text
Keep strain gauges unloaded for taring...
```
Each `read()` averages 8 fresh conversions per channel and produces, for each bridge:
```text
<name>_microstrain
<name>_mv           raw bridge output before taring
```
Example packet:
```json
{"sensor":"strain_1","timestamp":1791119904187,"values":{"strain_0_microstrain":512.4,"strain_0_mv":4.62},"valid":true}
```
Settings shared by all channels (oversampling, samples per reading, global chop, clock frequency and reference) are passed as a `StrainGaugeADCSettings`, whose defaults match the strain gauge PCB.
`valid` is false if any configured input is saturated. If that happens, lower the PGA gain.
Strain gauge test
`tests/test_strain_gauge.cpp` checks the driver and strain maths against a simulated ADS131M08, so it runs on any Linux machine without hardware:
```bash
g++ -std=c++17 tests/test_strain_gauge.cpp src/hardware/SPIBus.cpp src/hardware/GPIOInput.cpp src/hardware/ADS131M08.cpp src/sensors/SPISensor.cpp src/sensors/analog/StrainGaugeSensor.cpp -Isrc -Isrc/hardware -Isrc/sensors -Isrc/sensors/analog -o test_strain_gauge
./test_strain_gauge
```
Test status: the strain gauge code passes the simulated-device test but has not yet been run against a real ADS131M08.
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

│   ├── ADS131M08.cpp
│   ├── ADS131M08.h
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

g++ -std=c++17 src/main.cpp src/core/VCUController.cpp src/core/SensorManager.cpp src/config/SystemConfig.cpp src/communication/CommunicationManager.cpp src/data/DataSerialiser.cpp src/data/SensorReading.cpp src/hardware/I2CBus.cpp src/hardware/SPIBus.cpp src/hardware/GPIOInput.cpp src/hardware/ADS131M08.cpp src/sensors/I2CSensor.cpp src/sensors/SPISensor.cpp src/sensors/GyroscopeSensor.cpp src/sensors/analog/StrainGaugeSensor.cpp src/sensors/Camera.cpp -I. -Isrc -Isrc/core -Isrc/config -Isrc/communication -Isrc/data -Isrc/hardware -Isrc/sensors -Isrc/sensors/i2c -Isrc/sensors/analog -Isrc/util -pthread -o vcu

```
Run with:
```bash

./vcu

```
Stop with:
```text

Ctrl+C

```