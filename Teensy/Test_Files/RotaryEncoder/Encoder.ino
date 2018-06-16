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
  pinMode(encoderPinButton, INPUT);

  // enable pullup resistors on interrupt pins
  digitalWrite(encoderPinSignalA, HIGH);
  digitalWrite(encoderPinSignalB, HIGH);

  // call updateEncoder() when any change detected on pin 2/3 interrupt 0/1 pins 
  attachInterrupt(0, serviceEncoderInterrupt, CHANGE); 
  attachInterrupt(1, serviceEncoderInterrupt, CHANGE);
}

void loop(){ 
  if(volume != lastVolume) {
    Serial.println(volume);
    lastVolume = volume; // volume changed so update lastVolume. 
  }
  
  buttonVal = digitalRead(encoderPinButton);
  if(buttonVal == LOW && lastButtonState != buttonVal) {
    Serial.println("Button Pressed! Reset Encoder");
    volume = 0;
  }
  lastButtonState = buttonVal;    

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

/* Read Quadrature Encoder
  * Connect Encoder to Pins encoder0PinA, encoder0PinB, and +5V.
  *
  * Sketch by max wolf / www.meso.net
  * v. 0.1 - very basic functions - mw 20061220
  *
  


 int val; 
 int encoder0PinA = 3;
 int encoder0PinB = 4;
 int encoder0Pos = 0;
 int encoder0PinALast = LOW;
 int n = LOW;

 void setup() { 
   pinMode (encoder0PinA,INPUT);
   pinMode (encoder0PinB,INPUT);
   Serial.begin (9600);
 } 

 void loop() { 
   n = digitalRead(encoder0PinA);
   if ((encoder0PinALast == LOW) && (n == HIGH)) {
     if (digitalRead(encoder0PinB) == LOW) {
       encoder0Pos--;
     } else {
       encoder0Pos++;
     }
     Serial.print (encoder0Pos);
     Serial.print ("/");
   } 
   encoder0PinALast = n;
 } 


#define encoder0PinA 2
#define encoder0PinB 3

volatile unsigned int encoder0Pos = 0;

void setup() {

  pinMode(encoder0PinA, INPUT); 
  pinMode(encoder0PinB, INPUT); 
// encoder pin on interrupt 0 (pin 2)

  attachInterrupt(0, doEncoderA, CHANGE);
// encoder pin on interrupt 1 (pin 3)

  attachInterrupt(1, doEncoderB, CHANGE);  
  Serial.begin (57600);
}

void loop(){  }

void doEncoderA(){

  // look for a low-to-high on channel A
  if (digitalRead(encoder0PinA) == HIGH) { 
    // check channel B to see which way encoder is turning
    if (digitalRead(encoder0PinB) == LOW) {  
      encoder0Pos = encoder0Pos + 1;         // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
  }
  else   // must be a high-to-low edge on channel A                                       
  { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(encoder0PinB) == HIGH) {   
      encoder0Pos = encoder0Pos + 1;          // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
  Serial.println (encoder0Pos, DEC);          
  // use for debugging - remember to comment out
}

void doEncoderB(){

  // look for a low-to-high on channel B
  if (digitalRead(encoder0PinB) == HIGH) {   
   // check channel A to see which way encoder is turning
    if (digitalRead(encoder0PinA) == HIGH) {  
      encoder0Pos = encoder0Pos + 1;         // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
  }
  // Look for a high-to-low on channel B
  else { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(encoder0PinA) == LOW) {   
      encoder0Pos = encoder0Pos + 1;          // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
}

*/
