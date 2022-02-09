#include <FastLED.h>

// DIN              
#define  P_PREVIOUS_SONG  1
#define  P_PLAY_PAUSE     2
#define  P_NEXT_SONG      3
#define  P_SPOTIFY        4
#define  P_RADIO          5
#define  P_DOOR_PIN       6

// AIN              
#define  P_VOLUME         0
#define  P_CHANNEL        5

// DOUT             
#define  P_LED_DATA_1     12
#define  P_LED_DATA_2     11

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
// Mode
enum_mode  current_mode =     OFF;

// Volume
const int numReadings = 10;

int volume_readings[numReadings];
int  volume_read_index  =       0;
int  total_volume       =       0;
int  average            =       0;

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
	FastLED.addLeds<LED_TYPE, LED_DATA_1, COLOR_ORDER>(mode_leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
	FastLED.addLeds<LED_TYPE, LED_DATA_2, COLOR_ORDER>(bar_leds, NUM_LEDS).setCorrection( TypicalLEDStrip );
	FastLED.setBrightness(  BRIGHTNESS );
	setModeLED(1);
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
		sendSerialCommands(command, 2);
		// Is there any disadvantages of setting LEDs every cycle?
		// If not, move this line after the if-statement:
		setModeLED(current_mode);
	} 
	else if (digitalRead(P_RADIO) && current_mode != RADIO) {
		current_mode = RADIO;
		int command[] = {current_mode};
		sendSerialCommands(command, 2);
		setModeLED(current_mode);
	} 
	else if (!digitalRead(P_SPOTIFY) && !digitalRead(P_RADIO) && current_mode != OFF){
		current_mode = OFF;
		int command[] = {current_mode};
		sendSerialCommands(command, 2);
		setModeLED(current_mode);
	}
}

void updatePlaybackState(){
	enum_command  current_command  =  NONE;
	if (digitalRead(P_PREVIOUS_SONG)) { //Pause/play
		current_command = PREVIOUS_SONG
	} else if (digitalRead(P_PLAY_PAUSE)) { //Previous
		current_command = PLAY_PAUSE
	} else if(digitalRead(P_NEXT_SONG)){ //Next song
		current_command = NEXT_SONG
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
	volume_read_index = readIndex + 1;

	// if we're at the end of the array...
	if (volume_read_index >= numReadings) {
		volume_read_index = 0;
	}
	// calculate the average:
	average = total_volume / numReadings;

	if (average < currentVol - 3 || average > currentVol + 3 || currentVol < 0){
		currentVol = average; 
		int command[] = {current_mode, VOLUME_UPDATE, currentVol};
		sendSerialCommands(command, 2);
	}

}

void updateBarDoorState(){
	if (digitalRead(P_DOOR_PIN)){
		// Count the variable to add a delay to the light
		if (led_counter < 10 000) {
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

void sendSerialCommands(int command[]) {
	int len = sizeof(command) / sizeof(int)
	for (byte i = 0; i < len; i = i + 1) {
		Serial.print(command[i]);
		if(i != len-1) {
			Serial.print(',');        
		}
	}
	Serial.print('\n');
	delay(15);
}
