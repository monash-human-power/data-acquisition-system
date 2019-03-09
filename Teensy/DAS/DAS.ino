#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include <TinyGPS++.h> // https://github.com/mikalhart/TinyGPSPlus/releases
#include <SoftwareSerial.h>
#include "SPI.h"
#include "SensorStructures.h"

/* Debug Mode */
#define DEBUG // Comment this line out if not using debug mode
#define WAIT 60 // delay for teensy to start serial comms

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
static const int BUTTON_PIN = 5;
static const int RECORD_LED = 13;
static const int STATUS_LED = 12, WARNING_LED = 11 , ERROR_LED = 4;
static const int POT_PIN = A0;
static const int GPS_RXPin = 7, GPS_TXPin = 8;
#define RPISERIAL Serial2 // Pin 9 (RX) & PIN 10 (TX) for Teensy LC
//const int SDchipSelect = 10;
const int LMS6DS3chipSelect = 6;

// Set up Accelerometer
LSM6DS3 myIMU(SPI_MODE, LMS6DS3chipSelect);

// GPS Variables & Setup
static const uint32_t GPS_Baud = 9600;
TinyGPSPlus tinyGPS;
SoftwareSerial ss(GPS_RXPin, GPS_TXPin);

// Raspberry Pi Communication
// Fastest speed for Teensy LC before errors occuring
// See here: https://www.pjrc.com/teensy/td_uart.html
int rpi_baud_rate = 500000;   // Set baud rate to 500000

void setup()
{
  // Set Up Button Pin
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  // Set up LEDs
  pinMode(RECORD_LED, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);
  pinMode(WARNING_LED, OUTPUT);
  pinMode(ERROR_LED, OUTPUT);
  
  // Open serial communications and wait for port to open:
  Serial.begin(9600);
  // Open Raspberry Pi Serial communication
  RPISERIAL.begin(rpi_baud_rate, SERIAL_8N1/*8 Data bits, No Parity bits*/);  // Hardware Serial (RX & TX pins)

  DEBUG_PRINTLN("Waiting for Raspberry Pi to boot");
  int countdown = 0;
  while (countdown != WAIT) {
    led_blink(1000); // This takes 1 seconds
    countdown++;
    DEBUG_PRINTLN("Booting...");
  }
  
  // Nothing to do to set up POT

  // Set Up IMU
  SPI1.setMOSI(0);
  SPI1.setMISO(1);
  SPI1.setSCK(20);
  myIMU.begin();

  // Set Up GPS
  ss.begin(GPS_Baud);

  DEBUG_PRINTLN("Waiting for serial communication");
  digitalWrite(ERROR_LED, HIGH);
  while (true)
  {
    if (RPISERIAL.available())
    {
      DEBUG_PRINTLN("rpiserial.available");
      if(RPISERIAL.read())
      {
        DEBUG_PRINTLN("Serial communication established.");

        // Blink lights if communications established
        led_blink(1000);
        break;
      }
    }
  }
  digitalWrite(ERROR_LED, LOW);

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
      digitalWrite(STATUS_LED, HIGH);

      /* GPS */ 
      GPS gps;
      gps = getGPSData(tinyGPS);
      
      // Output GPS Data
      output_data += "gps=";
      if (gps.satellites > 0)
      {
        // Only disable red LED if GPS is working
        digitalWrite(ERROR_LED, LOW);
        output_data += "1";
        output_data += "&gps_location=" + String(gps.latitude, 4) + "," + String(gps.longitude, 4) + "," + String(gps.altitude, 4);
        output_data += "&gps_course=" + String(gps.course, 4);
        output_data += "&gps_speed=" + String(gps.speed, 4);
        output_data += "&gps_satellites=" + String(gps.satellites);
        DEBUG_PRINTLN("GPS DATA:");
        DEBUG_PRINTLN("Latitude = " + String(gps.latitude, 4));
        DEBUG_PRINTLN("Longitude = " + String(gps.longitude, 4));
        DEBUG_PRINTLN("Altitude = " + String(gps.altitude, 4));
        DEBUG_PRINTLN("Speed = " + String(gps.speed, 4));
        DEBUG_PRINTLN("Satellites = " + String(gps.satellites));
      }
      else
      {
        output_data += "0";
        DEBUG_PRINTLN("GPS DATA:\nNONE");

        // Show red LED when GPS is not working
        digitalWrite(ERROR_LED, HIGH);
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

      output_data += "&aX=" + String(accelerometer.x, 4);
      output_data += "&aY=" + String(accelerometer.y, 4);
      output_data += "&aZ=" + String(accelerometer.z, 4);

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

      output_data += "&gX=" + String(gyroscope.x, 4);
      output_data += "&gY=" + String(gyroscope.y, 4);
      output_data += "&gZ=" + String(gyroscope.z, 4);
      
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

      output_data += "&thermoC=" + String(temperature.celsius, 4);
      output_data += "&thermoF=" + String(temperature.fahrenheit, 4);

      /* Pot */
      String pot_data;
      pot_data = getPotData();

      DEBUG_PRINTLN("POTENTIOMETER DATA:");
      DEBUG_PRINTLN(pot_data);
      DEBUG_PRINTLN("");
      output_data += "&pot=" + pot_data;
      
      DEBUG_PRINTLN(output_data);
      writeStringToRPi(output_data);
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
  RPISERIAL.write("\n");
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
  digitalWrite(STATUS_LED, HIGH);
  delay(time_delay/2);
  digitalWrite(STATUS_LED, LOW);
  delay(time_delay);
}

void isrService()
{
  DEBUG_PRINTLN("ISR");
  button_state = digitalRead(BUTTON_PIN);
  if (button_state == 0)
  {
    if (is_recording == 0)
    {
    digitalWrite(RECORD_LED,!button_state);
    is_recording = 1;
    writeStringToRPi("start");
    DEBUG_PRINTLN("Start recording");
    }
    else
    {
      digitalWrite(RECORD_LED,button_state);
      is_recording = 0;
      writeStringToRPi("stop");
      DEBUG_PRINTLN("Stop recording");
    }
    delay(1000);
  }
}

