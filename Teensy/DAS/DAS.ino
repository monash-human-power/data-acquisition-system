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
      // Clear output string
      String output_data = "";
      
      // Indicate System is Working
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(RED_LED, LOW);

      /* GPS */ 
      String GPS_data;
      GPS_data = getGPSData(gps);
      
      // Output GPS Data
      DEBUG_PRINTLN("GPS DATA:\n" + GPS_data);
      output_data += "gps=" + GPS_data;
      
      /* Reed Switch */
      String reed_data;
      reed_data = getReedData();

      // Output Reed Data
      DEBUG_PRINTLN("REED DATA:\n" + reed_data);
      output_data += "&reed=" + reed_data;

      /* Accelerometer */
      Accelerometer accelerometer;
      accelerometer = getAccelerometerData(myIMU);

      // Output accelerometer data
      DEBUG_PRINTLN("ACCELEROMETER DATA:");
      DEBUG_PRINT("X = ");
      DEBUG_PRINT_DEC(accelerometer.x, 4);
      DEBUG_PRINT("\nY = ");
      DEBUG_PRINT_DEC(accelerometer.y, 4);
      DEBUG_PRINT("\nZ = ");
      DEBUG_PRINT_DEC(accelerometer.z, 4);
      DEBUG_PRINT("\n");

      output_data += "&aX=" + (String) accelerometer.x;
      output_data += "&aY=" + (String) accelerometer.y;
      output_data += "&aZ=" + (String) accelerometer.z;

      /* Gyroscope */
      Gyroscope gyroscope;
      gyroscope = getGyroscopeData(myIMU);
      
      // Output gyroscope data
      DEBUG_PRINTLN("GYROSCOPE DATA:");
      DEBUG_PRINT("X = ");
      DEBUG_PRINT_DEC(gyroscope.x, 4);
      DEBUG_PRINT("\nY = ");
      DEBUG_PRINT_DEC(gyroscope.y, 4);
      DEBUG_PRINT("\nZ = ");
      DEBUG_PRINT_DEC(gyroscope.z, 4);
      DEBUG_PRINT("\n");

      output_data += "&gX=" + (String) gyroscope.x;
      output_data += "&gY=" + (String) gyroscope.y;
      output_data += "&gZ=" + (String) gyroscope.z;
      
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

      output_data += "&thermoC=" + (String) temperature.celsius;
      output_data += "&thermoF=" + (String) temperature.fahrenheit;

      /* Pot */
      String pot_data;
      pot_data = getPotData();

      DEBUG_PRINTLN("POTENTIOMETER DATA:");
      DEBUG_PRINTLN(pot_data);
      DEBUG_PRINTLN("");
      output_data += "&pot=" + pot_data;

      writeStringToRPi(output_data);
      Serial.println(output_data);
    }
  }
}

/*
 * Function to write String variable type since Serial.write("input") does not allow String variable as input
 */
void writeStringToRPi(String stringData) 
{ 
  RPISERIAL.clear();
  for (int i = 0; i < stringData.length(); i++)
  {
    RPISERIAL.write(stringData[i]);
  }
}

String getGPSData(TinyGPSPlus gps)
{
  String output_data;
  int gps_date, gps_time, gps_satellites;
  double gps_latitude, gps_longitude, gps_altitude, gps_course, gps_speed;

  gps_latitude = gps.location.lat();
  gps_longitude = gps.location.lng();
  gps_altitude = gps.altitude.meters();
  gps_course = gps.course.value();
  gps_time = gps.time.value();
  gps_speed = gps.speed.kmph();
  gps_satellites = gps.satellites.value();

  if (gps_satellites > 0)
  {
    output_data = "1";
    output_data += "&gps_location=" + String(gps_latitude) + "," + String(gps_longitude) + "," + String(gps_altitude);
    output_data += "&gps_course=" + String(gps_course);
    output_data += "&gps_speed=" + String(gps_speed);
    output_data += "&gps_satellites=" + String(gps_satellites);
  }
  else
  {
    output_data = "0";
  }
  return output_data;
}

String getReedData()
{
  String output_data;
  int proximity = digitalRead(REED_PIN); // Read the state of the switch
  if (proximity == LOW) // If the pin reads low, the switch is closed.
  {
    output_data = "1";
  }
  else
  {
    output_data = "0";
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
  return pot;
}

