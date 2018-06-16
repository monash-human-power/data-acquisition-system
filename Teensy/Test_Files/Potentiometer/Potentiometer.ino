void setup()
{                
  Serial.begin(1000000);
}

int val;

void loop()                     
{
  val = analogRead(0);
  Serial.print("analog 0 is: ");
  Serial.println(val);
  delay(10);
}
