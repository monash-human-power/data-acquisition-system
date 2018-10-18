#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include <TinyGPS++.h> // https://github.com/mikalhart/TinyGPSPlus/releases
#include <SoftwareSerial.h>
#include "SPI.h"
#include "SensorStructures.h"

/* Debug Mode */
#define DEBUG // Comment this line out if not using debug mode
#define WAIT 0 // delay for teensy to start serial comms

/* Variables for edge trigger */
int previous = 0;
int next = 0;

/* Variables for interrupts */
volatile int is_recording = 0;
volatile int button_state = 0;

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
static const int BUTTON_PIN = 2; // Pin connected to reed switch
static const int GREEN_LED = 4, RED_LED = 3;
static const int POT_PIN = 0;
static const int GPS_RXPin = 7, GPS_TXPin = 8;
const int LMS6DS3chipSelect = 6;

// Set up Accelerometer
LSM6DS3 myIMU(SPI_MODE, LMS6DS3chipSelect);

// GPS Variables & Setup
static const uint32_t GPS_Baud = 9600;
TinyGPSPlus tinyGPS;
SoftwareSerial ss(GPS_RXPin, GPS_TXPin);

void setup()
{
  // Set Up Button Pin
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Set up LEDs
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  
  // Nothing to do to set up POT

  // Set Up IMU
  SPI1.setMOSI(0);
  SPI1.setMISO(1);
  SPI1.setSCK(20);
  myIMU.begin();

  // Set Up GPS
  ss.begin(GPS_Baud);
  
  // Set up interrupts
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(BUTTON_PIN, isrService, CHANGE); // interrrupt 1 is data ready
  sei();
}

void loop()
{
  // Service GPS
  if ((ss.available() > 0) and (is_recording == 1))
  {
    if (tinyGPS.encode(ss.read()))
    {
      // Clear output string
      String output_data = "";
      
      // Indicate System is Working
      digitalWrite(GREEN_LED, HIGH);
      digitalWrite(RED_LED, LOW);

      /* GPS */ 
      GPS gps;
      gps = getGPSData(tinyGPS);
      
      // Output GPS Data
      output_data += "gps=";
      if (gps.satellites > 0)
      {
        output_data += "1";
        output_data += "&gps_location=" + String(gps.latitude) + "," + String(gps.longitude) + "," + String(gps.altitude);
        output_data += "&gps_course=" + String(gps.course);
        output_data += "&gps_speed=" + String(gps.speed);
        output_data += "&gps_satellites=" + String(gps.satellites);
        DEBUG_PRINTLN("GPS DATA:");
        DEBUG_PRINTLN("Latitude = " + String(gps.latitude));
        DEBUG_PRINTLN("Longitude = " + String(gps.longitude));
        DEBUG_PRINTLN("Altitude = " + String(gps.altitude));
        DEBUG_PRINTLN("Speed = " + String(gps.speed));
        DEBUG_PRINTLN("Satellites = " + String(gps.satellites));
      }
      else
      {
        output_data += "0";
        DEBUG_PRINTLN("GPS DATA:\nNONE");

        // Show red LED when GPS is not working
        digitalWrite(RED_LED, HIGH);
      }

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

      DEBUG_PRINTLN(output_data);
    }     
  }
}

GPS getGPSData(TinyGPSPlus gps)
{
  GPS GPS_data;

  // Store data
  GPS_data.latitude = gps.location.lat();
  GPS_data.longitude = gps.location.lng();
  GPS_data.altitude = gps.altitude.meters();
  GPS_data.course = gps.course.value();
  GPS_data.time = gps.time.value();
  GPS_data.speed = gps.speed.kmph();
  GPS_data.satellites = gps.satellites.value();

  return GPS_data;
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

void led_blink(int time_delay) 
{
  digitalWrite(GREEN_LED, HIGH);
  digitalWrite(RED_LED, HIGH);
  delay(time_delay/2);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);
  delay(time_delay);
}

void isrService()
{
  button_state = digitalRead(BUTTON_PIN);
  if (button_state == 0)
  {
    if (is_recording == 0)
    {
    digitalWrite(GREEN_LED,!button_state);
    digitalWrite(RED_LED,!button_state);
    is_recording = 1;
    DEBUG_PRINTLN("Start recording");
    }
    else
    {
      digitalWrite(GREEN_LED,button_state);
      digitalWrite(RED_LED,button_state);
      is_recording = 0;
      DEBUG_PRINTLN("Stop recording");
    }
    delay(1000);
  }
}

