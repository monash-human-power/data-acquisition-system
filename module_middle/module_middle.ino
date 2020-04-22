#include <WiFi.h>
#include <PubSubClient.h>
#include "DHT.h"
#include <stdio.h>
#include <Wire.h>
#include <ArduinoJson.h>

#define DHTPIN 4      // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22

// Update these with values suitable for your network.
const char* ssid = "<INSERT WIFI NETWORK>";
const char* password = "<INSERT WIFI PASSWORD>";
const char* mqtt_server = "tailor.cloudmqtt.com";
#define mqtt_port 13072
#define MQTT_USER "<MQTT USERNAME>"
#define MQTT_PASSWORD "<MQTT PASSWORD>"
#define MQTT_SERIAL_PUBLISH_CH "esp/test"
#define MQTT_SERIAL_RECEIVER_CH "esp/test"
#define anInput 19
int co2Zero;

//IMU Pin Connection
//SCL - D22
//SDA - D21
const int MPU_addr=0x68; // I2C address of the MPU-6050
int16_t AcX,AcY,AcZ,Tmp,GyX,GyY,GyZ;

DHT dht(DHTPIN, DHTTYPE);
WiFiClient wifiClient;

PubSubClient client(wifiClient);

void setup_wifi() {
    delay(10);
    // We start by connecting to a WiFi network
   // Serial.println();
   // Serial.print("Connecting to ");
   // Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    randomSeed(micros());
   // Serial.println("");
   // Serial.println("WiFi connected");
   // Serial.println("IP address: ");
   //  Serial.println(WiFi.localIP());

  //  Serial.println(F("DHTxx test!"));

    dht.begin();

}

void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    // Create a random client ID
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    // Attempt to connect
    if (client.connect(clientId.c_str(),MQTT_USER,MQTT_PASSWORD)) {
      Serial.println("connected");
      //Once connected, publish an announcement...
      client.publish("esp/test", "hello world");
      // ... and resubscribe
      client.subscribe(MQTT_SERIAL_RECEIVER_CH);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte *payload, unsigned int length) {
    Serial.println("-------new message from broker-----");
    Serial.print("channel:");
    Serial.println(topic);
    Serial.print("data:");
    Serial.write(payload, length);
    Serial.println();
}
// ----------------------- //
// CO2 sensor calibration
// ----------------------- //
int calibrate() {
  Serial.print("\n");
  Serial.println("----------------------");
  Serial.print("Calibrating the sensor");
  Serial.print("\n");

  int CO2_zero = 1;
  int CO2_cal[20];
  int tmp = 0;


  for (int x = 0;x<20;x++){                   //samplpe co2 10x over 2 seconds
    CO2_cal[x]=analogRead(anInput);
    delay(1000);
  }

  for (int x = 0;x<20;x++){                     //add samples together
    tmp=tmp + CO2_cal[x];
  }

  int cal = (tmp/20) - CO2_zero;

  while (cal != 0)
  {
    CO2_zero += 1;
    cal = (tmp/20) - CO2_zero;
  }
  Serial.println("----------------------");
  Serial.print("Calibrating Done!");
  Serial.print("\n");
  Serial.print("----------------------");

  return CO2_zero;
}

void setup() {
  //Setting up IMU
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0); // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  //Code for the rest
  Serial.begin(115200);
  Serial.setTimeout(500);// Set time out for
  setup_wifi();
    co2Zero = calibrate();
  pinMode(anInput,INPUT);
  delay(1000);

  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
  reconnect();
}

void publishSerialData(char *serialData){
  if (!client.connected()) {
    reconnect();
  }
  client.publish(MQTT_SERIAL_PUBLISH_CH, serialData);
}
void loop() {

   client.loop();
   if (Serial.available() > 0) {
     char mun[501];
     memset(mun,0, 501);
     Serial.readBytesUntil( '\n',mun,500);
     publishSerialData(mun);
   }

  delay(2000);
   int co2now[10];                               //int array for co2 readings
  int co2raw = 0;                               //int for raw value of co2
  int co2comp = 0;                              //int for compensated co2
  int co2ppm = 0;                               //int for calculated ppm
  int tmp = 0;
  char str[4];

  for (int x = 0;x<10;x++){
    co2now[x]=analogRead(anInput);
    delay(100);
  }

  for (int x = 0;x<10;x++){
      tmp=tmp + co2now[x];
    }

  co2raw = tmp/10;                            //divide samples by 10
  co2comp = co2raw - co2Zero;                 //get compensated value
  co2ppm = map(co2comp,0,1023,400,5000);      //map value for atmospheric levels
  itoa(co2ppm, str, 10);

   //  client.loop();
   //Initiating the buffer
   StaticJsonBuffer<300> jsonBuffer;

   //The main data structure
   JsonObject& WirelessMod = jsonBuffer.createObject();
   WirelessMod["module-id"]= 2;
   JsonArray& sensors = WirelessMod.createNestedArray("sensors");
   //Making CO2JSON
   JsonObject& CO2val = jsonBuffer.createObject();

   CO2val["type"]= "CO2";
   CO2val["value"]= co2ppm;
  //Serial.print("\n");
  // Serial.print(str);
  // client.publish("esp/co2", str);
  // Serial.print("\n");
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();

  //Making humidJSON
   JsonObject& HUMIDval = jsonBuffer.createObject();
   HUMIDval["type"]= "Humidity";
   HUMIDval["value"]= h;

  // Read temperature as Celsius (the default)

  float t = dht.readTemperature();
  //Making tempJSON
  JsonObject& TEMPval = jsonBuffer.createObject();
  TEMPval["type"]= "Temp";
  TEMPval["value"]= t;

  // Check if any reads failed and exit early (to try again).
  if (isnan(h) || isnan(t) ) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  //saving data
  //int tempData[2] ;
  //char strtemp[20];    //create an empty string to store number
  // sprintf(strtemp, "%f", t);



  //client.publish("esp/temp",strtemp);

//IMU CODE
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B); // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true); // request a total of 14 registers



  AcX=Wire.read()<<8|Wire.read(); // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY=Wire.read()<<8|Wire.read(); // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read(); // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  GyX=Wire.read()<<8|Wire.read(); // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY=Wire.read()<<8|Wire.read(); // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ=Wire.read()<<8|Wire.read(); // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)
  //Creating Acceleration JSON
    JsonObject& ACCELval = jsonBuffer.createObject();
    ACCELval["type"]="accelerometer"
   JsonObject& innerSensor = CO2val.createNestedObject("value");
   innerSensor["x"]=AcX;
   innerSensor["y"]=AcY;
   innerSensor["z"]=AcZ;
   //Creating Gyroscope JSON
    JsonObject& GYROval = jsonBuffer.createObject();
    ACCELval["type"]="gyroscope"
   JsonObject& innerSensor = CO2val.createNestedObject("value");
   innerSensor["x"]=GyX;
   innerSensor["y"]=GyY;
   innerSensor["z"]=GyZ;
   JsonArray& sensors = WirelessMod.createNestedArray("sensors");
   sensors.add(CO2val);
   sensors.add(TEMPval);
   sensors.add(HUMIDval);
   sensors.add(ACCELval);
   sensors.add(GYROval);






  /**
  Serial.print("AcX = "); Serial.print(AcX);
  Serial.print(" | AcY = "); Serial.print(AcY);
  Serial.print(" | AcZ = "); Serial.print(AcZ);
  Serial.print(" | Tmp = "); Serial.print(Tmp/340.00+36.53); //equation for temperature in degrees C from datasheet
  Serial.print(" | GyX = "); Serial.print(GyX);
  Serial.print(" | GyY = "); Serial.print(GyY);
  Serial.print(" | GyZ = "); Serial.println(GyZ); **/

  delay(333);


 }
