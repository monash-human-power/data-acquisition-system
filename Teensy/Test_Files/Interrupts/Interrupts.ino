static const int BUTTON_PIN = 2; // Pin connected to reed switch
static const int GREEN_LED = 4, RED_LED = 3;

int count = 0;
int start_recording = 0;
int button_state = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  pinMode(BUTTON_PIN, INPUT_PULLUP);
  attachInterrupt(BUTTON_PIN, isrService, CHANGE); // interrrupt 1 is data ready

  // Set up LEDs
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  // Enable global interrupts
  sei();
}

void loop() 
{
  // Do pointless things
  while (true)
  {
    count++;
  }
}

void isrService()
{
  button_state = digitalRead(BUTTON_PIN);
  if (button_state == 0)
  {
    if (start_recording == 1)
    {
    digitalWrite(GREEN_LED,!button_state);
    digitalWrite(RED_LED,!button_state);
    start_recording = 0;
    }
    else
    {
      digitalWrite(GREEN_LED,button_state);
      digitalWrite(RED_LED,button_state);
      start_recording = 1;
    }
    delay(1000);
  }
}
