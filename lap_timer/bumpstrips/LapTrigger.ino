
// Messages to be sent to python script
const string START_MESSAGE = "Start Message";
const string LAP_MESSAGE = "Lap Message";

const int TRIGGER_DELAY = 1000; // Delay to avoid unwanted tiggers (e.g. second wheel of bike)
const int bumpStripPin = 2; // Pin connected to bump strip


int buttonState = 0; 
bool timerStarted = false;

// Arduino setup
void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);
}

void loop() 
{
  int buttonState = digitalRead(buttonPin);

  if (buttonState == LOW) {
        if (~started){
            Serial.println(START_MESSAGE);
            timerStarted = true;
        }
        else{
            Serial.println(LAP_MESSAGE);
        }

    delay(TRIGGER_DELAY)
  }
  
  
  
}
