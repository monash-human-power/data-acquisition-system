#include <TinyGPS++.h>
#include <WiFi.h>
#include <PubSubClient.h>

// add json

// CO2 Sensor parameters
#define RLOAD 10.0
#define RZERO 18.35
#define PARA 116.6020682
#define PARB 2.769034857

// Parameters to model temperature and humidity dependence
#define CORA 0.00035
#define CORB 0.02718
#define CORC 1.39538
#define CORD 0.0018

// Atmospheric CO2 level for calibration purposes
#define ATMOCO2 400

class MQ135 {
 private:
  int _pin;

 public:
  MQ135(int pin);
  float getCorrectionFactor(float t, float h);
  float getResistance();
  float getCorrectedResistance(float t, float h);
  float getPPM();
  float getCorrectedPPM(float t, float h);
  float getRZero();
  float getCorrectedRZero(float t, float h);
};

MQ135::MQ135(int pin) {
  _pin = pin;
}

float MQ135::getCorrectionFactor(float t, float h) {
  return CORA * t * t - CORB * t + CORC - (h-33.)*CORD;
}

float MQ135::getResistance() {
  int val = analogRead(_pin);
  return ((1023./(float)val) * 5. - 1.)*RLOAD;
}

float MQ135::getCorrectedResistance(float t, float h) {
  return getResistance()/getCorrectionFactor(t, h);
}

float MQ135::getPPM() {
  return PARA * pow((getResistance()/RZERO), -PARB);
}

float MQ135::getCorrectedPPM(float t, float h) {
  return PARA * pow((getCorrectedResistance(t, h)/RZERO), -PARB);
}

float MQ135::getRZero() {
  return getResistance() * pow((ATMOCO2/PARA), (1./PARB));
}

float MQ135::getCorrectedRZero(float t, float h) {
  return getCorrectedResistance(t, h) * pow((ATMOCO2/PARA), (1./PARB));
}


// MQTT variables
const char* ssid = "Lak";
const char* password = "qwerty123";
const char* mqtt_server = "soldier.cloudmqtt.com";
#define mqtt_port 11989
#define MQTT_USER "punbssjf"
#define MQTT_PASSWORD "N5R0WZ4gQD9y"
bool start_stop = false;

WiFiClient wifiClient;

PubSubClient client(wifiClient);

// ----------------------- //
// MQTT functions
// ----------------------- //
void setup_wifi() {
    delay(10);
    // We start by connecting to a WiFi network
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
    if (topic == "/v3/wireless-module/3/start")
    {
        start_stop = true;
        Serial.println("-------Start Data Tx-----");
    }
    else if (topic == "/v3/wireless-module/3/stop")
    {
        start_stop = false;
        Serial.println("-------Stop Data Tx-----");
    }
}

// GPS sensor instantiation
#define RXD2 16
#define TXD2 17
TinyGPSPlus gps;

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


// ----------------------- //
// Reed functions
// ----------------------- //
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

void get_vel_dis(int numberOfInterrupts)
{
  // Calculate velocity and distance
  VELOCITY = (1/t_time) * PI * WHEEL_DIAMETER * 3600;
  DISTANCE = numberOfInterrupts * WHEEL_DIAMETER;

  Serial.println("New ping: ");
  Serial.println(t_time);
  Serial.println(DISTANCE);
  Serial.println(VELOCITY);
}

//initialise CO2 sensor : pin 34
MQ135 co2Sensor(34);

void setup() {
  Serial.begin(115200);

//   setup_wifi();

//   client.setServer(mqtt_server, mqtt_port);
//   client.setCallback(callback);

//   Serial2.begin(9600, SERIAL_8N1, RXD2, TXD2); // gps

//   pinMode(reedPin, INPUT_PULLUP); // reed
//   attachInterrupt(digitalPinToInterrupt(reedPin), handleInterrupt, FALLING);

   
// while (!client.connected()) {
//     Serial.println("Connecting to MQTT...");
 
//     if (client.connect("ESP32Client", MQTT_USER, MQTT_PASSWORD )) {
 
//       Serial.println("connected");  
 
//     } else {
 
//       Serial.print("failed with state ");
//       Serial.print(client.state());
//       Serial.println();
//       delay(2000);
 
//     }
//   }

}

void loop() {

  // if(interruptCounter>0)
  // {
  //     portENTER_CRITICAL(&mux);
  //     interruptCounter--;
  //     portEXIT_CRITICAL(&mux);

  //     numberOfInterrupts++;

  //     get_vel_dis(numberOfInterrupts);
  // }

  // float ppm = co2Sensor.getPPM();
  // gps.encode(Serial2.read());

  // Serial.print("LAT =");  Serial.println(gps.location.lat(), 6);
  // Serial.print("LONG ="); Serial.println(gps.location.lng(), 6);
  // Serial.print("ALT =");  Serial.println(gps.altitude.meters());
  // Serial.print("CO2 PPM =");  Serial.println(ppm);
  // delay(1000);

  // client.loop();

}
