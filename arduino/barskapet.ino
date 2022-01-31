#include <FastLED.h>

// DIN              
#define  P_PREVIOUS_SONG  1
#define  P_PLAY_PAUSE     2
#define  P_NEXT_SONG      3
#define  P_SPOTIFY        4
#define  P_RADIO          5

// AIN              
#define  P_VOLUME         0
#define  P_CHANNEL        5

// DOUT             
#define  P_LED_DATA_1     12
#define  P_LED_DATA_2     11

// LEDS:            
#define  NUM_LEDS         18
#define  BRIGHTNESS       50
#define  LED_TYPE         WS2811
#define  COLOR_ORDER      GRB

// COMMAND ENUM
enum command {
	NONE,
	VOLUME_UPDATE,
	NEXT_SONG,
	PLAY_PAUSE,
	PREVIOUS_SONG,
	CHANNEL_UPDATE
};

// MODE ENUM
enum command {
	OFF,
	SPOTIFY,
	RADIO
};

// VARIABLES
command  current_command  =  NONE;
command  current_mode     =  NONE;

// Volume
int measVol = 0;
int vol = 0;
int currentVol = -1;

// Playback
int   playbackEnabled  =  false;
int   currentPlaylist  =  0;
int   plCounter        =  0;
long  timeAvg          =  0.0;

//LED inside shelf
int ledState = 0;
const int ledPin = A7;
int ledCounter = 0;
int ledVal = 0;

//Mode                
int currentState       = -1; 

// LEDS CONFIG
CRGB leds[NUM_LEDS]; //Leds for mode 
CRGB leds2[NUM_LEDS]; //Leds for shelf
CRGBPalette16 currentPalette;
TBlendType    currentBlending;
extern CRGBPalette16 myRedWhiteBluePalette;
extern const TProgmemPalette16 myRedWhiteBluePalette_p PROGMEM;

void setup() {
  Serial.begin(9600);
  
  // LED SETUP
  delay( 3000 ); // power-up safety delay
  FastLED.setMaxPowerInVoltsAndMilliamps(5,800); 
  FastLED.addLeds<LED_TYPE, LED_DATA_1, COLOR_ORDER>(leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.addLeds<LED_TYPE, LED_DATA_2, COLOR_ORDER>(leds2, NUM_LEDS).setCorrection( TypicalLEDStrip );
  FastLED.setBrightness(  BRIGHTNESS );
  setAll(1);
}

void loop() {
  if(analogRead(P_SPOTIFY) > 500 && currentState != 1) {
    currentState = 1;
    int values[] = {currentState, 1, -1};
    printValues(values, 2);
    setAll(0);
    
  } else if (analogRead(P_RADIO) > 500 && currentState != 2) {
    currentState = 2;
    int values[] = {currentState, 2, -1};
    printValues(values, 2);
    setAll(2);
  } else if (analogRead(P_SPOTIFY) < 500 && analogRead(P_RADIO) < 500 && currentState != 0){
      currentState = 0;
      int values[] = {currentState, 1, -1};   
      printValues(values, 2);
      reset(0);

  }

  switch (currentState)
  {
  case 1:
    //getPlaylist();
    getPlaybackControl();  
    break;

  case 2:
    getPlaybackControl();
    break;
    //TODO
  default:
    break;
  }

  measVol = 100*(double)analogRead(P_VOLUME)/(double)1024;
  if (ledCounter < 20) {
    vol += measVol;
  }else{
    measVol = 100 - vol/20;
    if ((measVol < currentVol - 3 || measVol > currentVol + 3 || currentVol  < 0) && !playbackEnabled){
      currentVol = measVol; 
      int values[] = {4, measVol};
      printValues(values, 2);
    }
    vol = 0;
  }
  
  if (ledCounter < 20) {
    ledVal += analogRead(ledPin);
    ledCounter += 1;
  } else {
      ledVal = ledVal/20;
      ledCounter = 0;
      if (ledVal > 500 && ledState == 0) {
        delay(500);
        setAll(1);
        ledState = 1;
      }
      else {
        if(ledState && !ledVal) {
          reset(1);
          ledState = 0;
        }
      }
      ledVal = 0;
  }
}


void getPlaybackControl(){
    int Pvalues[] = {currentState}; //ID2 is for playback
    if (analogRead(P_PLAY_PAUSE) > 100) { //Pause/play
      Pvalues[1] = 1;
    } else if (analogRead(P_PREVIOUS_SONG) > 100) { //Previous
      Pvalues[1] = 0;
    } else if(analogRead(P_NEXT_SONG) > 100){ //Next song
      Pvalues[1] = 2;
    } else {
      playbackEnabled = false;
      return;
    }
    printValues(Pvalues, 2);
    playbackEnabled = true; 
}


void setAll(int mode) {
  //0 Spotify
  //1 barskapet
  //2 .....
  
  switch(mode){ 
    case 0:
      for(int i = 0; i < NUM_LEDS; i++ ) {
        leds[i] = CRGB::Green;
      }
      break;
    case 1: 
      for(int i = 0; i < NUM_LEDS; i++ ) {
        leds2[i] = CRGB::Orange;
      }
      break;
    case 2:
      for(int i = 0; i < NUM_LEDS; i++ ) {
          leds[i] = CRGB::Red;
        }
        break;
  }
  FastLED.show();
}

void reset(int stripnr) {
  switch(stripnr){ 
    case 0:
      for(int i = 0; i < NUM_LEDS; i++ ) {
        leds[i] = CRGB::Black;
      }
      break;
    case 1: 
      for(int i = 0; i < NUM_LEDS; i++ ) {
        leds2[i] = CRGB::Black;
      }
      break;
  }
  FastLED.show();
}

void printValues(int values[], int len) {
  for (byte i = 0; i < len; i = i + 1) {
      Serial.print(values[i]);
      if(i != len-1) {
        Serial.print(',');        
      }
    }
   Serial.print('\n');
   delay(15);
}

