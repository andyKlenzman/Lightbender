//Compatable (or atleast trying to be) w/ com 5.2
//Features: Two Hand Compatability
/*
- switch between palettes 
- three control modes 
- three pattern modes

*/





#include <FastLED.h>

#define DATA_PIN 33
#define CLK_PIN 32
#define LED_TYPE SK9822 
#define COLOR_ORDER BGR
#define NUM_LEDS 150
int BRIGHTNESS = 255;
CRGB leds[NUM_LEDS];

static boolean recvInProgress = false;
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// variables to hold the parsed data
int x = 0;
int y = 0;
int z = 0;
int h = 0;

const int rows = 6;
const int cols = 2;
int rdata[rows][cols] = { { 1, 2}, { 3, 4}, { 5, 6}, { 7, 8}, { 9, 10}, { 11, 12}};
int ldata[rows][cols] = { { 1, 2}, { 3, 4}, { 5, 6}, { 7, 8}, { 9, 10}, { 11, 12}};

boolean newData = false;

//button class
#define buttonPin 15
int buttonState;

bool noResistor;
bool pullupActivated;

//for debounce
unsigned long lastTimeStateChanged;
unsigned long debounceDelay;

//for button functionality
unsigned long lastStateChange;
unsigned long resetTimer=1000;
int buttonCounter;
int lastButtonState = 1;
int cmd;



//for integration of patterns and handcontrols



void setup() {
  // put your setup code here, to run once:
  Serial.begin(500000);


  FastLED.addLeds<LED_TYPE, DATA_PIN, CLK_PIN, COLOR_ORDER>(leds, NUM_LEDS);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear();
  FastLED.show();

  pinMode(buttonPin, INPUT_PULLUP);
//  attachInterrupt(digitalPinToInterrupt(15), reader, CHANGE);
//could possibly use an interrupt to run the button (though why not just use the ir 
//remote at this point. 



}

void loop() {
  reader();  
  settings();
  runLights();
  runModes();



  
  recvWithStartEndMarkers();
  if (newData == true) {
    strcpy(tempChars, receivedChars);
    // this temporary copy is necessary to protect the original data
    //   because strtok() used in parseData() replaces the commas with \0
    parseData();
    printer();
    newData = false;
  }
  
    FastLED.show();
  
  

}

//============



void recvWithStartEndMarkers() {
  static boolean recvInProgress = false;
  static byte ndx = 0;
  char startMarker = '<';
  char endMarker = '>';
  char rc;

  while (Serial.available() > 0 && newData == false) {
    rc = Serial.read();

    if (recvInProgress == true) {
      if (rc != endMarker) {
        receivedChars[ndx] = rc;
        ndx++;
        if (ndx >= numChars) {
          ndx = numChars - 1;
        }
      }
      else {
        receivedChars[ndx] = '\0'; // terminate the string
        recvInProgress = false;
        ndx = 0;
        newData = true;
      }
    }

    else if (rc == startMarker) {
      recvInProgress = true;
    }
  }
}

//============

void parseData() {      // split the data into its parts

  char * strtokIndx; // this is used by strtok() as an index

  strtokIndx = strtok(tempChars, ",");      // get the first part - the string
  h = atoi(strtokIndx); // copy it to messageFromPC

  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  z = atoi(strtokIndx); 
  
  strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
  x = atoi(strtokIndx);     // convert this part to an integer

  strtokIndx = strtok(NULL, ",");
  y = atoi(strtokIndx);     // convert this part to a float

  //sorts into two seperate arrays based on l/r hand
  if(h==0){
  ldata[z][0] = x;
  ldata[z][1] = y;
  }
  
  if(h==1){
  rdata[z][0] = x;
  rdata[z][1] = y;
  }
}

//============




//button stuff
void reader(){
  unsigned long timeNow = millis();
  if(timeNow - lastTimeStateChanged > debounceDelay){
    byte newState = digitalRead(buttonPin);
    if (newState != buttonState){
      buttonState = newState;
      lastTimeStateChanged=timeNow;
    }
  }
  buttonState = digitalRead(buttonPin);
  if(buttonState == 1){
  }
  if(buttonState == 0){
  }
}

byte settings(){
  
  //each time the button is pressed
  //the buttonCounter adds one and
  //the resetTimer is reset to 0
 
  unsigned long timeNow=millis();
  if(buttonState != lastButtonState){
    if(buttonState == 1){
      buttonCounter++;
      lastStateChange = timeNow;
    }   
  }

  //The resetTimer that bumps the buttonCounter
  //back to zero and sets cmd to the number of
  //buttons pressed between 1-3
  
  if(timeNow - lastStateChange > resetTimer){
    if(buttonCounter>0 && buttonCounter<4){
        cmd = buttonCounter;
    }
      buttonCounter=0;
      lastStateChange = timeNow;
      
      }
  lastButtonState = buttonState;
}
