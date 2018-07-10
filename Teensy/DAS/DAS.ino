#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include <SD.h>
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include "SPI.h"

// Pin Values
static const int REED_PIN = 2; // Pin connected to reed switch
static const int GREEN_LED = 3, RED_LED = 4;
static const int POT_PIN = 0;
static const int GPS_RXPin = 7, GPS_TXPin = 8;
//const int SDchipSelect = 10;
const int LMS6DS3chipSelect = 6;

// Set up Accelerometer
LSM6DS3 myIMU(SPI_MODE, LMS6DS3chipSelect);

// GPS Variables & Setup
static const uint32_t GPS_Baud = 9600;
TinyGPSPlus gps;
SoftwareSerial ss(GPS_RXPin, GPS_TXPin);

// Variables
float ax;
float ay;
float az;
float gx;
float gy;
float gz;
float tempC;
float tempF;
int pot;
int gps_date;
int gps_time;
int gps_satellites;
double gps_latitude;
double gps_longitude;
double gps_altitude;
double gps_course;
double gps_speed;
String GPS_Data;

void setup() 
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);

  // Set Up Reed Switch
  pinMode(REED_PIN, INPUT_PULLUP);
  
  // Set up LEDs
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  // Indicate system is until it works
  // change functionality here later on to indicate communication with pi
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, HIGH);

  // Nothing to do to set up POT
  
  // Set Up IMU
  SPI1.setMOSI(0);
  SPI1.setMISO(1);
  SPI1.setSCK(20);
  myIMU.begin();

  // Set Up GPS
  ss.begin(GPS_Baud);
}


void loop()
{
  // Service GPS
  if (ss.available() > 0)
  {
    if (gps.encode(ss.read()))
    {
      // Indicate System is Working
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(RED_LED, LOW);
      
      // Get GPS Information
      gps_latitude = gps.location.lat();
      gps_longitude = gps.location.lng();
      gps_altitude = gps.altitude.meters();
      gps_course = gps.course.value();
      gps_time = gps.time.value();
      gps_speed = gps.speed.kmph();
      gps_satellites = gps.satellites.value();

      if (gps_satellites > 0)
      {
        GPS_Data = "Location = " + String(gps_latitude) + ", " + String(gps_longitude) + ", " + String(gps_altitude) + "\n";
        GPS_Data += "Course = " + String(gps_course) + "\n";
        GPS_Data += "Speed = " + String(gps_speed) + "\n";
        GPS_Data += "Satellites = " + String(gps_satellites) + "\n";
        GPS_Data += "\n";
      }
      else
      {
        GPS_Data = "No Data\n\n";
      }

      Serial.println("GPS DATA:");
      Serial.print(GPS_Data);

      /// Service Reed Switch
      Serial.print("REED SWITCH:\n");
      int proximity = digitalRead(REED_PIN); // Read the state of the switch
      if (proximity == LOW) // If the pin reads low, the switch is closed.
      {
        Serial.println("Switch = 1");
      }
      else
      {
        Serial.println("Switch = 0");
      }

      // Service Accelerometer
      Serial.print("\nACCELEROMETER:\n");
      Serial.print(" X = ");
      ax = myIMU.readFloatAccelX();
      Serial.println(ax, 4);
      
      Serial.print(" Y = ");
      ay = myIMU.readFloatAccelY();
      Serial.println(ay, 4);
      
      Serial.print(" Z = ");
      az = myIMU.readFloatAccelZ();
      Serial.println(az, 4);
    
      // Service Gyroscope
      Serial.print("\nGYROSCOPE:\n");
      Serial.print(" X = ");
      gx = myIMU.readFloatGyroX();
      Serial.println(gx, 4);
      Serial.print(" Y = ");
      gy = myIMU.readFloatGyroY();
      Serial.println(gy, 4);
      Serial.print(" Z = ");
      gz = myIMU.readFloatGyroZ();
      Serial.println(gz, 4);
    
      // Service Thermometer
      Serial.print("\nTHERMOMETER:\n");
      Serial.print(" Degrees C = ");
      tempC = myIMU.readTempC();
      Serial.println(tempC, 4);
      Serial.print(" Degrees F = ");
      tempF = myIMU.readTempF();
      Serial.println(tempF, 4);
    
      // Service Pot
      Serial.print("\nPOTENTIOMETER:");
      pot = analogRead(POT_PIN);
      Serial.print("\nPot = ");
      Serial.println(pot);
      Serial.print("\n");
    }
  }
}

