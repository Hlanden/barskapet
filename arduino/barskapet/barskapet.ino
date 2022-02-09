#include <FastLED.h>

// DIN              
#define  P_PREVIOUS_SONG  2
#define  P_PLAY_PAUSE     3
#define  P_NEXT_SONG      4
#define  P_SPOTIFY        7
#define  P_RADIO          8
#define  P_DOOR_PIN       9

// AIN              
#define  P_VOLUME         0
#define  P_CHANNEL        1

// DOUT             
#define  P_LED_DATA_1     5
#define  P_LED_DATA_2     6

// LEDS            
#define  NUM_LEDS         18
#define  BRIGHTNESS       50
#define  LED_TYPE         WS2811
#define  COLOR_ORDER      GRB

// COMMAND ENUM
enum enum_command {
	NONE,
	VOLUME_UPDATE,
	NEXT_SONG,
	PLAY_PAUSE,
	PREVIOUS_SONG,
	CHANNEL_UPDATE
};

// MODE ENUM
enum enum_mode {
	OFF,
	SPOTIFY,
	RADIO
};

// VARIABLES
// Key repeat rate in milli seconds
const int key_repeat_rate = 500;
unsigned long previous_key_time = 0;
// Mode
enum_mode  current_mode =     OFF;

// Volume
const int numReadings   =      20;

int volume_readings[numReadings];
int  volume_read_index  =       0;
int  total_volume       =       0;
int  average            =       0;
int  current_volume     =      -1;

// LED inside shelf
int  bar_led_state      =       0;
int  led_counter        =       0;
int  ledVal             =       0;

// LEDS CONFIG
CRGB           mode_leds[NUM_LEDS];
CRGB           bar_leds[NUM_LEDS];
CRGBPalette16  currentPalette;
TBlendType     currentBlending;
extern CRGBPalette16 myRedWhiteBluePalette;
extern const TProgmemPalette16 myRedWhiteBluePalette_p PROGMEM;

void setup() {
	Serial.begin(9600);
	// SET I/O PINS

	// Input
	pinMode(P_PREVIOUS_SONG,  INPUT);
	pinMode(P_PLAY_PAUSE,     INPUT);
	pinMode(P_NEXT_SONG,      INPUT);
	pinMode(P_SPOTIFY,        INPUT);
	pinMode(P_RADIO,          INPUT);
	pinMode(P_DOOR_PIN,       INPUT);

	// Output
	pinMode(P_LED_DATA_1,     OUTPUT);
	pinMode(P_LED_DATA_2,     OUTPUT);

	// VOLUME SETUP
	for (int thisReading = 0; thisReading < numReadings; thisReading++) {
		volume_readings[thisReading] = 0;
	}

	// LED SETUP
	delay( 3000 ); // power-up safety delay
	FastLED.setMaxPowerInVoltsAndMilliamps(5,800); 
	FastLED.addLeds<LED_TYPE, P_LED_DATA_1, COLOR_ORDER>(mode_leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
	FastLED.addLeds<LED_TYPE, P_LED_DATA_2, COLOR_ORDER>(bar_leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
	FastLED.setBrightness(  BRIGHTNESS );
	setModeLED(OFF);
}

void loop() {
	// MODE
	updateModeState();

	// PLAYBACK
	updatePlaybackState();

	// VOLUME
	updateVolumeState();

	// LED INSIDE THE BAR
	updateBarDoorState();
}

void updateModeState(){
	if(digitalRead(P_SPOTIFY) && current_mode != SPOTIFY) {
		current_mode = SPOTIFY;
		int command[] = {current_mode};
		sendSerialCommands(command, 1);
		// Is there any disadvantages of setting LEDs every cycle?
		// If not, move this line after the if-statement:
		setModeLED(current_mode);
	} 
	else if (digitalRead(P_RADIO) && current_mode != RADIO) {
		current_mode = RADIO;
		int command[] = {current_mode};
		sendSerialCommands(command, 1);
		setModeLED(current_mode);
	} 
	else if (!digitalRead(P_SPOTIFY) && !digitalRead(P_RADIO) && current_mode != OFF){
		current_mode = OFF;
		int command[] = {current_mode};
		sendSerialCommands(command, 1);
		setModeLED(current_mode);
	}
}

void updatePlaybackState(){
	enum_command  current_command  =  NONE;
  if (millis() - previous_key_time > key_repeat_rate) {
    if (digitalRead(P_PREVIOUS_SONG)) { //Pause/play
    current_command = PREVIOUS_SONG;
    previous_key_time = millis();
  } else if (digitalRead(P_PLAY_PAUSE)) { //Previous
    current_command = PLAY_PAUSE;
    previous_key_time = millis();
  } else if(digitalRead(P_NEXT_SONG)){ //Next song
    current_command = NEXT_SONG;
    previous_key_time = millis();
  }
  }
	

	if (current_command != NONE && current_mode != OFF) {
		int command[] = {current_mode, current_command};
		sendSerialCommands(command, 2);
	}
}

void updateVolumeState(){
	// Using smoothing algorithm to calculate volume: 
	// https://www.arduino.cc/en/Tutorial/BuiltInExamples/Smoothing
	total_volume = total_volume - volume_readings[volume_read_index];
	volume_readings[volume_read_index] = 100 * (double) analogRead(P_VOLUME) / (double) 1024;
	total_volume = total_volume + volume_readings[volume_read_index];
	volume_read_index = volume_read_index + 1;

	// if we're at the end of the array...
	if (volume_read_index >= numReadings) {
		volume_read_index = 0;
	}
	// calculate the average:
  // I have switched ground and 5V in the cabinet, so it needs to be inverted...
	average = 100 - total_volume / numReadings;

	if (average < current_volume - 7 || average > current_volume + 7 || current_volume < 0){
		current_volume = average; 
		int command[] = {current_mode, VOLUME_UPDATE, current_volume};
		sendSerialCommands(command, 3);
	}

}

void updateBarDoorState(){
	if (digitalRead(P_DOOR_PIN)){
		// Count the variable to add a delay to the light
		if (led_counter < 5000) {
			led_counter += 1;
		}
		else {
			turnOnBarLED();
			led_counter = 0;
		}
	}
	else {
		led_counter = 0;
		turnOffBarLED();
	}
}

void setModeLED(enum_mode mode) {
	switch(mode){ 
		case OFF:
			for(int i = 0; i < NUM_LEDS; i++ ) {
				mode_leds[i] = CRGB::Black;
			}
			break;
		case SPOTIFY: 
			for(int i = 0; i < NUM_LEDS; i++ ) {
				mode_leds[i] = CRGB::Green;
			}
			break;
		case RADIO:
			for(int i = 0; i < NUM_LEDS; i++ ) {
				mode_leds[i] = CRGB::Red;
			}
			break;
	}
	FastLED.show();
}

void turnOnBarLED() {
	if (!bar_led_state){
		bar_led_state = true;
		for(int i = 0; i < NUM_LEDS; i++ ) {
			bar_leds[i] = CRGB::Orange;
		}
		FastLED.show();
	}
}

void turnOffBarLED() {
	if (bar_led_state){
		bar_led_state = false;
		for(int i = 0; i < NUM_LEDS; i++ ) {
			bar_leds[i] = CRGB::Black;
		}
		FastLED.show();
	}
}

void sendSerialCommands(int command[], int len) {
	for (byte i = 0; i < len; i = i + 1) {
		Serial.print(command[i]);
		if(i != len-1) {
			Serial.print(',');        
		}
	}
	Serial.print('\n');
	delay(15);
}
