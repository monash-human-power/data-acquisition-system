#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include <TinyGPS++.h>
#include <SoftwareSerial.h>
#include "SPI.h"

/* Debug Mode */
#define DEBUG // Comment this line out if not using debug mode

#ifdef DEBUG
  #define DEBUG_PRINTLN(input_text) Serial.println(input_text);
  #define DEBUG_PRINT_DEC(input_text, text_length) Serial.print(input_text, text_length);
  #define DEBUG_PRINT(input_text) Serial.print(input_text);
#else
   #define DEBUG_PRINTLN(input_text)
  #define DEBUG_PRINT_DEC(input_text, text_length)
  #define DEBUG_PRINT(input_text)
#endif

// Pin Values
static const int REED_PIN = 2; // Pin connected to reed switch
static const int GREEN_LED = 3, RED_LED = 4;
static const int POT_PIN = 0;
static const int GPS_RXPin = 7, GPS_TXPin = 8;
#define RPISERIAL Serial2 // Pin 9 (RX) & PIN 10 (TX) for Teensy LC
//const int SDchipSelect = 10;
const int LMS6DS3chipSelect = 6;

// Set up Accelerometer
LSM6DS3 myIMU(SPI_MODE, LMS6DS3chipSelect);

// GPS Variables & Setup
static const uint32_t GPS_Baud = 9600;
TinyGPSPlus gps;
SoftwareSerial ss(GPS_RXPin, GPS_TXPin);

// Raspberry Pi Communication
// Fastest speed for Teensy LC before errors occuring
// See here: https://www.pjrc.com/teensy/td_uart.html
int rpi_baud_rate = 500000;   // Set baud rate to 500000


// Define structs
struct Accelerometer
{
  float x;
  float y;
  float z;
};

struct Gyroscope
{
  float x;
  float y;
  float z;
};

struct Temperature
{
  float celsius;
  float fahrenheit;
};

// Global Variables
int gps_date, gps_time, gps_satellites;
double gps_latitude, gps_longitude, gps_altitude, gps_course, gps_speed;

void setup()
{
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  // Open Raspberry Pi Serial communication
  RPISERIAL.begin(rpi_baud_rate, SERIAL_8N1/*8 Data bits, No Parity bits*/);  // Hardware Serial (RX & TX pins)

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

      /* GPS */ 
      String GPS_Data;
      GPS_Data = getGPSData(gps);
      
      // Output GPS Data
      DEBUG_PRINTLN("GPS DATA:\n" + GPS_Data);
      RPISERIAL.write("GPS DATA:\n");
      writeStringToRPi(GPS_Data);
      RPISERIAL.flush();
      
      /* Reed Switch */
      String reed_Data;
      reed_Data = getReedData();

      // Output Reed Data
      DEBUG_PRINTLN("REED DATA:\n" + reed_Data);
      RPISERIAL.write("REED DATA:\n");
      writeStringToRPi(reed_Data);
      RPISERIAL.flush();

      /* Accelerometer */
      Accelerometer accelerometer;
      accelerometer = getAccelerometerData(myIMU);

      // Output accelerometer data
      DEBUG_PRINTLN("ACCELEROMETER DATA:");
      DEBUG_PRINT("X = ");
      DEBUG_PRINT_DEC(accelerometer.x, 4);
      DEBUG_PRINT("Y = ");
      DEBUG_PRINT_DEC(accelerometer.y, 4);
      DEBUG_PRINT("Z = ");
      DEBUG_PRINT_DEC(accelerometer.z, 4);
      DEBUG_PRINT("\n\n");
      
      RPISERIAL.write("ACCELEROMETER DATA:\n");
      RPISERIAL.write("X = ");
      writeStringToRPi(accelerometer.x);
      RPISERIAL.write(" Y = ");
      writeStringToRPi(accelerometer.y);
      RPISERIAL.write(" Z = ");
      writeStringToRPi(accelerometer.z);
      RPISERIAL.write("\n");

      /* Gyroscope */
      Gyroscope gyroscope;
      gyroscope = getGyroscopeData(myIMU);
      
      // Output gyroscope data
      DEBUG_PRINTLN("GYROSCOPE DATA:");
      DEBUG_PRINT("X = ");
      DEBUG_PRINT_DEC(gyroscope.x, 4);
      DEBUG_PRINT("Y = ");
      DEBUG_PRINT_DEC(gyroscope.y, 4);
      DEBUG_PRINT("Z = ");
      DEBUG_PRINT_DEC(gyroscope.z, 4);
      DEBUG_PRINT("\n");

      RPISERIAL.write("GYROSCOPE DATA:\n");
      RPISERIAL.write("X = ");
      writeStringToRPi(gyroscope.x);
      RPISERIAL.write(" Y = ");
      writeStringToRPi(gyroscope.y);
      RPISERIAL.write(" Z = ");
      writeStringToRPi(gyroscope.z);
      RPISERIAL.write("\n");
      
      /* Thermometer */
      Temperature temperature;
      temperature = getTemperatureData(myIMU);
      
      // Output thermometer data
      DEBUG_PRINTLN("THERMOMETER DATA:");
      DEBUG_PRINT("Celsius = ");
      DEBUG_PRINT_DEC(temperature.celsius, 4);
      DEBUG_PRINT(" Fahrenheit = ");
      DEBUG_PRINT_DEC(temperature.fahrenheit, 4);
      DEBUG_PRINT("\n");

      RPISERIAL.write("THERMOMETER DATA:\n");
      RPISERIAL.write("Celsius = ");
      writeStringToRPi(temperature.celsius);
      RPISERIAL.write(" Fahrenheit = ");
      writeStringToRPi(temperature.fahrenheit);
      RPISERIAL.write("\n");

      /* Pot */
      String pot_data;
      pot_data = getPotData();

      DEBUG_PRINTLN("POTENTIOMETER DATA:\n");
      DEBUG_PRINTLN(pot_data);

      RPISERIAL.write("POTENTIOMETER DATA:\n");
      writeStringToRPi(pot_data);
      RPISERIAL.write("\n");      
    }
  }
}

/*
 * Function to write String variable type since Serial.write("input") does not allow String variable as input
 */
void writeStringToRPi(String stringData) 
{ 
  for (int i = 0; i < stringData.length(); i++)
  {
    RPISERIAL.write(stringData[i]);
  }
}

String getGPSData(TinyGPSPlus gps)
{
  String output_data;
  
  gps_latitude = gps.location.lat();
  gps_longitude = gps.location.lng();
  gps_altitude = gps.altitude.meters();
  gps_course = gps.course.value();
  gps_time = gps.time.value();
  gps_speed = gps.speed.kmph();
  gps_satellites = gps.satellites.value();

  if (gps_satellites > 0)
  {
    output_data = "Location = " + String(gps_latitude) + ", " + String(gps_longitude) + ", " + String(gps_altitude) + "\n";
    output_data += "Course = " + String(gps_course) + "\n";
    output_data += "Speed = " + String(gps_speed) + "\n";
    output_data += "Satellites = " + String(gps_satellites) + "\n";
    output_data += "\n";
  }
  else
  {
    output_data = "No Data\n";
  }
  return output_data;
}

String getReedData()
{
  String output_data;
  int proximity = digitalRead(REED_PIN); // Read the state of the switch
  if (proximity == LOW) // If the pin reads low, the switch is closed.
  {
    output_data = "Switch = 1\n";
  }
  else
  {
    output_data = "Switch = 0\n";
  }
  return output_data;
}

Accelerometer getAccelerometerData(LSM6DS3 input_IMU)
{
  Accelerometer accelerometer; 

  accelerometer.x = myIMU.readFloatAccelX();
  accelerometer.y = myIMU.readFloatAccelY();
  accelerometer.z = myIMU.readFloatAccelZ();
  return accelerometer;
}

Gyroscope getGyroscopeData(LSM6DS3 input_IMU)
{
  Gyroscope gyroscope; 

  gyroscope.x = myIMU.readFloatGyroX();
  gyroscope.y = myIMU.readFloatGyroY();
  gyroscope.z = myIMU.readFloatGyroZ();
  return gyroscope;
}

Temperature getTemperatureData(LSM6DS3 input_IMU)
{
  Temperature temperature;
  temperature.celsius = myIMU.readTempC();
  temperature.fahrenheit = myIMU.readTempF();
  return temperature;
}

String getPotData()
{
  int pot;
  pot = analogRead(POT_PIN);
  
  String output_data = "POT = ";
  output_data += pot ;
  output_data += "\n";
  return output_data;
}

