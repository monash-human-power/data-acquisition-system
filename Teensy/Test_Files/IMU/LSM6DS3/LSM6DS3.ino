/******************************************************************************
MinimalistExample.ino

Marshall Taylor @ SparkFun Electronics
May 20, 2015
https://github.com/sparkfun/LSM6DS3_Breakout
https://github.com/sparkfun/SparkFun_LSM6DS3_Arduino_Library

Description:
Most basic example of use.

Example using the LSM6DS3 with basic settings.  This sketch collects Gyro and
Accelerometer data every second, then presents it on the serial monitor.

Resources:
Uses Wire.h for i2c operation
Uses SPI.h for SPI operation
Either can be omitted if not used

Development environment specifics:
Arduino IDE 1.6.4
Teensy loader 1.23

Hardware connections:
Connect I2C SDA line to A4
Connect I2C SCL line to A5
Connect GND and 3.3v power to the IMU

This code is released under the [MIT License](http://opensource.org/licenses/MIT).

Please review the LICENSE.md file included with this example. If you have any questions 
or concerns with licensing, please contact techsupport@sparkfun.com.

Distributed as-is; no warranty is given.
******************************************************************************/

#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include "SPI.h"

// Set pins
const int LED_OUTPUT = 13;
const int CHIP_SELECT = 10;
const int SCK_PIN = 20;
const int MISO_PIN = 1;
const int MOSI_PIN = 0;

// Set IMU to use SPI and make pin 10 to be the chip select pin
LSM6DS3 myIMU(SPI_MODE, CHIP_SELECT);  // CS output to pin 10
//LSM6DS3 myIMU; //Default constructor is I2C, addr 0x6B

void setup() {
  
  // Set pins
  pinMode(LED_OUTPUT, OUTPUT);
  // put your setup code here, to run once:
  Serial.begin(9600);
  delay(1000); //relax...
  Serial.println("Processor came out of reset.\n");

  // Set new SPI pins
  // *** Each device is different, change assigned pins above (Below tested with Teensy 3.6) ***
  SPI1.setMOSI(MOSI_PIN);  // MOSI output to pin 0
  SPI1.setMISO(MISO_PIN);  // MISO output to pin 1
  SPI1.setSCK(SCK_PIN);  // SCK output to pin 20
  
  //Call .begin() to configure the IMU
  if(myIMU.begin() != 0){
    Serial.println("Problem starting sensor...");
    Serial.println("Check wiring connections\n");  
  }
  
}


void loop()
{
  //Get all parameters
  Serial.print("\nAccelerometer:\n");
  Serial.print(" X = ");
  Serial.println(myIMU.readFloatAccelX(), 4);
  Serial.print(" Y = ");
  Serial.println(myIMU.readFloatAccelY(), 4);
  Serial.print(" Z = ");
  Serial.println(myIMU.readFloatAccelZ(), 4);

  Serial.print("\nGyroscope:\n");
  Serial.print(" X = ");
  Serial.println(myIMU.readFloatGyroX(), 4);
  Serial.print(" Y = ");
  Serial.println(myIMU.readFloatGyroY(), 4);
  Serial.print(" Z = ");
  Serial.println(myIMU.readFloatGyroZ(), 4);

  Serial.print("\nThermometer:\n");
  Serial.print(" Degrees C = ");
  Serial.println(myIMU.readTempC(), 4);
  Serial.print(" Degrees F = ");
  Serial.println(myIMU.readTempF(), 4);

  // Blink LED when data has been 'sent'
  delay(10);
  digitalWrite(LED_OUTPUT, HIGH);
  delay(10);
  digitalWrite(LED_OUTPUT, LOW);
}
