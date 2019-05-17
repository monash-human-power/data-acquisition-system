#include "SparkFunLSM6DS3.h"
#include "Wire.h"
#include <TinyGPS++.h> // https://github.com/mikalhart/TinyGPSPlus/releases
#include <SoftwareSerial.h>
#include "SPI.h"
#include "SensorStructures.h"

/* Useful variables */
#define PI 3.1415926535897932384626433832795

/* Debug Mode */
#define DEBUG // Comment this line out if not using debug mode
#define WAIT 10 // delay for teensy to start serial comms

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
static const int REED_SWITCH_PIN = 2;
static const int BUTTON_PIN = 5;
static const int RECORD_LED = 13;
static const int STATUS_LED = 12, WARNING_LED = 11 , ERROR_LED = 4;
static const int POT_PIN = A0;
static const int GPS_RXPin = 7, GPS_TXPin = 8;
#define RPISERIAL Serial2 // Pin 9 (RX) & PIN 10 (TX) for Teensy LC
//const int SDchipSelect = 10;
const int LMS6DS3chipSelect = 6;

// Set up reed switch
volatile unsigned long PREV_REED_SWITCH_TIME = 0;
volatile unsigned long REED_SWITCH_COUNTER = 0;
volatile unsigned long PREV_REED_SWITCH_COUNT = 0;
volatile float VELOCITY = 0, DISTANCE = 0;

// 700C Rims + 33mm tyre
const float WHEEL_DIAMETER = 0.622 + (0.033 * 2);
const float WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER * PI;
IntervalTimer reedSwitchTimer;

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
  // Set up Reed Switch
  pinMode(REED_SWITCH_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(REED_SWITCH_PIN), reedSwitchInterruptHandler, FALLING); // interrrupt 1 is data ready
  // Check if stopped every 3 seconds
  reedSwitchTimer.begin(reedSwitchChecker, 3 * 1000000);

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
  attachInterrupt(digitalPinToInterrupt(BUTTON_PIN), switchInterruptHandler, CHANGE); // interrrupt 1 is data ready
  sei();
}

void loop()
{
  // Service GPS
  if (is_recording == 1)
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
    output_data += "0";
    DEBUG_PRINTLN("GPS DATA:\nNONE");

    // Show red LED when GPS is not working
    digitalWrite(ERROR_LED, HIGH);

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

    /* Reed Switch */
    DEBUG_PRINTLN("REED SWITCH DATA:");
    DEBUG_PRINTLN("Velocity:");
    DEBUG_PRINT_DEC(VELOCITY, 4);
    DEBUG_PRINTLN("");
    DEBUG_PRINTLN("Distance:");
    DEBUG_PRINT_DEC(DISTANCE, 4);
    DEBUG_PRINTLN("");
    output_data += "&reed_velocity=" + String(VELOCITY, 4);
    output_data += "&reed_distance=" + String(DISTANCE, 4);

    DEBUG_PRINTLN(output_data);
    writeStringToRPi(output_data);
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

volatile unsigned long last_switch_time = 0; // Don't leave Teensy running for more than 49 days..
void switchInterruptHandler()
{
  unsigned long total_time = millis() - last_switch_time;
  long max_debounce_time = 50;
  // Software debouncer
  if (total_time < max_debounce_time) {
    return;
  }
 
  last_switch_time = millis();
  button_state = digitalRead(BUTTON_PIN);
  if (button_state == 1 && is_recording == 0)
  {
    is_recording = 1;
    digitalWrite(RECORD_LED, HIGH);
    DEBUG_PRINTLN("ON");
    writeStringToRPi("start");
  } else if (button_state == 0 && is_recording == 1) {
    is_recording = 0;
    digitalWrite(RECORD_LED, LOW);
    DEBUG_PRINTLN("OFF");
    writeStringToRPi("stop");
  }
}

void reedSwitchInterruptHandler() {
  if(is_recording != 1) {
    return;
  }
  // Get start time
  if(PREV_REED_SWITCH_TIME == 0) {
    PREV_REED_SWITCH_TIME = millis();
    VELOCITY = 0;
    return;
  }
  unsigned long current_time = millis();
  unsigned long total_time = current_time - PREV_REED_SWITCH_TIME;
  // 50ms means we have a maximum velocity of 180km/h with a wheel diameter of 0.8
  if(total_time <= 50) {
    return;
  }

  // Count how many times wheel rotates
  REED_SWITCH_COUNTER = REED_SWITCH_COUNTER + 1;

  // Calculate velocity and distance
  VELOCITY = (1/(float)total_time) * PI * WHEEL_DIAMETER * 3600;
  DISTANCE = REED_SWITCH_COUNTER * WHEEL_CIRCUMFERENCE;
  PREV_REED_SWITCH_TIME = current_time;
}

// Check if the bike has stopped
void reedSwitchChecker() {
  if(is_recording != 1) {
    return;
  }
  if(PREV_REED_SWITCH_COUNT != REED_SWITCH_COUNTER) {
    PREV_REED_SWITCH_COUNT = REED_SWITCH_COUNTER;
  } else {
    // Stopped!
    noInterrupts();
    PREV_REED_SWITCH_TIME = 0;
    VELOCITY = 0;
    interrupts();
  }  
}

