#include "TM1637.h"

#define LED_PIN RED_LED

#define CLK_PIN      40
#define DIO_PIN      39

#define BUZZER_PIN   23

#define LIGHT_SENSOR 24

int lightValue = 0;
int ambientLightThreshold = 1400;
bool lightTurnedOn = false;
bool ignoreAmbientLight = false;

TM1637 tm1637(CLK_PIN, DIO_PIN);

int8_t displayTime[4];

unsigned long timerLength = 0;
bool timerCompleted = false;
unsigned long now = 0;
unsigned long last = 0;
char timerBuffer[32];

int length = 3;
char notes[] = "dew";
int beats[] = { 2, 2, 2 };
int tempo = 200;
char names[] = { 'c', 'd', 'e', 'f', 'w', 'g', 'a', 't', 'b', 'C' };
int tones[] = { 1915, 1700, 1519, 1432, 1354, 1275, 1136, 1075, 1014, 956 };

char specialEndingCharacter = '\n';

void setDisplayTime(unsigned long time_ms) {
  unsigned long seconds = time_ms / 1000;
  unsigned long minutes = (seconds / 60) % 60;
  unsigned long hours = seconds / 3600;
  seconds -= 60 * minutes;
  
  memset(displayTime, 0, 4);

  if (hours > 0) {
    if (hours < 10) {
      displayTime[0] = 0;
      displayTime[1] = hours;
    } else {
      displayTime[0] = hours / 10;
      displayTime[1] = hours % 10;
    }

    if (minutes < 10) {
      displayTime[2] = 0;
      displayTime[3] = minutes;
    } else {
      displayTime[2] = minutes / 10;
      displayTime[3] = minutes % 10;
    }
  } else if (minutes > 0) {
    displayTime[0] = minutes / 10;
    displayTime[1] = minutes % 10;
    displayTime[2] = seconds / 10;
    displayTime[3] = seconds % 10;
  } else {
    displayTime[0] = 0;
    displayTime[1] = 0;
    displayTime[2] = seconds / 10;
    displayTime[3] = seconds % 10;
  }

  for (int i = 0; i < 4; i++) {
    tm1637.display(i, displayTime[i]);
  }
}

void setup() {
  Serial.begin(9600);
  
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  tm1637.init();
  tm1637.set(BRIGHT_TYPICAL);

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {
  lightValue = analogRead(LIGHT_SENSOR);
  
  now = millis();
  
  if (Serial.available()) {
    String incomingString = Serial.readStringUntil(specialEndingCharacter);

    if (incomingString == "cancel_timer") {
      timerLength = 0;
    } else if (incomingString.startsWith("timer=")) {
      // We do 6 b/c len("timer=") = 6
      timerLength = incomingString.substring(6).toInt();
      last = now;
      return;
    } else if (incomingString == "light_on") {
      digitalWrite(LED_PIN, HIGH);
      lightTurnedOn = true;
    } else if (incomingString == "light_off") {
      digitalWrite(LED_PIN, LOW);
      lightTurnedOn = false;
    } else if (incomingString == "ignore_ambient_light") {
      ignoreAmbientLight = true;
    } else if (incomingString == "factor_ambient_light") {
      ignoreAmbientLight = false;
    }
  }

  if (timerLength > 0) {
    unsigned long diff = now - last;
    if (diff >= 1000) {
      if (timerLength <= 1000) {
        timerCompleted = true;
        timerLength = 0;
        setDisplayTime(0);
      } else {
        timerLength -= 1000;
        setDisplayTime(timerLength);
        memset(timerBuffer, 0, sizeof(timerBuffer));
        snprintf(timerBuffer, sizeof(timerBuffer), "timer=%lu\n", timerLength);
        Serial.write(timerBuffer);
      }
      last = now;
    }
    digitalWrite(LED_PIN, HIGH);
  }

  if (timerCompleted) {
    Serial.write("timer_finished\n");
    for(int i = 0; i < length; i++) {
      playNote(notes[i], beats[i] * tempo);
      delay(tempo / 2);
    }
    timerCompleted = false;
    lightTurnedOn = false;
    digitalWrite(LED_PIN, LOW);
  }

  if (ignoreAmbientLight) {
    return;
  }

  if (lightValue > ambientLightThreshold) {
    digitalWrite(LED_PIN, LOW);
  }
  
  if (lightValue < ambientLightThreshold && lightTurnedOn) {
    digitalWrite(LED_PIN, HIGH);
  }
}

void playTone(int tone, int duration) {
  for (long i = 0; i < duration * 1000L; i += tone * 2) 
  {
    digitalWrite(BUZZER_PIN, HIGH);
    delayMicroseconds(tone);
    digitalWrite(BUZZER_PIN, LOW);
    delayMicroseconds(tone);
  }
}

void playNote(char note, int duration) {
  for (int i = 0; i < 10; i++) {
    if (names[i] == note) {
      playTone(tones[i], duration);
    }
  }
}
