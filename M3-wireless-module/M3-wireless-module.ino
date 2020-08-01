#include <TinyGPS++.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "header.h"
//#include "string.h"

// output json data for publishing
const char* json_1 = "{\"sensors\":[{\"type\":\"co2\",\"value\":%.1f},{\"type\":\"reedVelocity\",\"value\":%.1f}]}";
const char* json_2 = "{\"sensors\":[{\"type\":\"gps\",\"value\":{\"latitude\":%.3f,\"longitude\":%.3f,\"altitude\":%.1f}}]}";
char data_1[110];
char data_2[110];
String data_message;

// MQTT variables
const char* ssid = "Slow Wifi";
const char* password = "5gqzkv7bpb";
const char* mqtt_server = "soldier.cloudmqtt.com";
#define mqtt_port 11989
#define MQTT_USER "punbssjf"
#define MQTT_PASSWORD "N5R0WZ4gQD9y"
bool start_stop = false;

// Reed Switch variables
static const int reedPin = 5;
volatile int interruptCounter = 0;
volatile int numberOfInterrupts = 0;
volatile unsigned long lastDebounceTime = 0;  // the last time the output pin was toggled
volatile unsigned long debounceDelay = 10;    // the debounce time; increase if the output flickers
volatile double total_time;
volatile double t_time;
volatile float VELOCITY = 0, DISTANCE = 0;

// 700C Rims + 33mm tyre
const float WHEEL_DIAMETER = 0.622 + (0.033 * 2);

//ISR intializer
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

// object initialisations
WiFiClient wifiClient;
PubSubClient client(wifiClient); 
TinyGPSPlus gps;                  // initialise tiny gps object
MQ135 co2Sensor(34);              // initialise CO2 sensor : pin 34


// ----------------------- //
//     MQTT functions      //
// ----------------------- //
// connect to wifi
void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    randomSeed(micros());
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

// callback for start / stop
void callback(char* topic, byte *payload, unsigned int length) {
  String strTopic = String((char*)topic);
  if(strTopic == "/v3/wireless-module/3/start") start_stop = true;
  else if (strTopic == "/v3/wireless-module/3/stop") start_stop = false;
}


// ----------------------- //
//      Reed functions     //
// ----------------------- //
// Interrupt Service Routine
void IRAM_ATTR handleInterrupt() {
  
  portENTER_CRITICAL(&mux);

  if (lastDebounceTime == 0)
  {
    lastDebounceTime = millis();
    VELOCITY = 0;
  }
  unsigned long current_time = millis();
  
  total_time = current_time - lastDebounceTime;
  
  if ((total_time) > debounceDelay) {
    interruptCounter++;
    t_time = total_time;
  }

  lastDebounceTime = current_time;
  portEXIT_CRITICAL(&mux);
}

// Calculate velocity and distance
void get_vel_dis(int numberOfInterrupts)
{
  VELOCITY = (1/t_time) * PI * WHEEL_DIAMETER * 3600;
  DISTANCE = numberOfInterrupts * WHEEL_DIAMETER;
}

void setup() {
  Serial.begin(115200);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  
  Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); // gps
 
  
  pinMode(reedPin, INPUT_PULLUP); // reed i/o for attaching ISR
  attachInterrupt(digitalPinToInterrupt(reedPin), handleInterrupt, FALLING);

  while (!client.connected()) {
      Serial.println("Connecting to MQTT...");
  
      if (client.connect("ESP32Client", MQTT_USER, MQTT_PASSWORD )) {
  
        Serial.println("..connected..");
        client.subscribe("/v3/wireless-module/3/start");
        client.subscribe("/v3/wireless-module/3/stop");
        Serial.println("Subscribed to topic");  
  
      } else {
  
        Serial.print("failed with state ");
        Serial.print(client.state());
        Serial.println();
        delay(2000);
  
      }
    }
    
}

void loop() {

  if(interruptCounter>0)
  {
      portENTER_CRITICAL(&mux);
      interruptCounter--;
      portEXIT_CRITICAL(&mux);

      numberOfInterrupts++;

      get_vel_dis(numberOfInterrupts);
  }

  float ppm = co2Sensor.getPPM();
  gps.encode(Serial2.read());
  delay(1000);
  
  if (start_stop)
  {
    // create json and publish on /v3/wireless-module/3/data
    sprintf(data_1, json_1, ppm, VELOCITY);
    sprintf(data_2, json_2, 32, 2, gps.location.lat(), gps.location.lng(), gps.altitude.meters(), 2);
    Serial.println(data_1);
    Serial.println(data_2);
    
    client.publish("/v3/wireless-module/3/data", data_1);
    client.publish("/v3/wireless-module/3/data", data_2);
  }

 client.loop();

}
