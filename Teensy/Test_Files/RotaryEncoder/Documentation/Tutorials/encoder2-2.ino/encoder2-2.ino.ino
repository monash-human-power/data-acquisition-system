// Rotary Encoder Code using interrupts

// Pins 2/3 are specific as they are interrupt pins
int encoderPinSignalA = 2;
int encoderPinSignalB = 3;
int encoderPinButton  = 4;

long lastVolume = 0;
 
// Volatile variables because our interrupt routine changes these variables
volatile long volume = 0; 
volatile int lastEncoded = 0;
 
int buttonVal,
    lastButtonState = 0;

void setup() {
  // initialize the serial monitor
  Serial.begin (57600);

  // set out input pins as inputs
  pinMode(encoderPinSignalA, INPUT); 
  pinMode(encoderPinSignalB, INPUT);

  // enable pullup resistors on interrupt pins
  digitalWrite(encoderPinSignalA, HIGH);
  digitalWrite(encoderPinSignalB, HIGH);

  // call updateEncoder() when any change detected on pin 2/3 interrupt 0/1 pins 
  attachInterrupt(0, serviceEncoderInterrupt, CHANGE); 
  attachInterrupt(1, serviceEncoderInterrupt, CHANGE);
}

void loop(){ 
  if(volume != lastVolume) 
  {
    Serial.println(volume);
    lastVolume = volume; // volume changed so update lastVolume. 
  }

  // Acts as rudimentary software button debouncing 
  delay(60);
}


void serviceEncoderInterrupt() {
  int signalA = digitalRead(encoderPinSignalA);
  int signalB = digitalRead(encoderPinSignalB);

  int encoded = (signalB << 1) | signalA;  // converting the 2 pin value to single number
  int sum  = (lastEncoded << 2) | encoded; // adding it to the previous encoded value

  if(sum == 0b0001 || sum == 0b0111 || sum == 0b1110 || sum == 0b1000) volume ++;
  if(sum == 0b0010 || sum == 0b1011 || sum == 0b1101 || sum == 0b0100) volume --;

  lastEncoded = encoded; // store this value for next time
}
