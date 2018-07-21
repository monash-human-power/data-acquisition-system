int reed_pin = 2;
float now;
int next_value, previous_value;

void setup() 
{
  Serial.begin(9600);
  Serial.println("Speed (km/hr)");
  pinMode(reed_pin, INPUT_PULLUP);
}

void loop() 
{
  next_value = digitalRead(reed_pin);
  //Serial.println(next_value);

  if ((next_value != previous_value) & next_value == 0)
  {
    now = micros();
    Serial.println(now);
  }

  previous_value = next_value;
  delayMicroseconds(50);
}
