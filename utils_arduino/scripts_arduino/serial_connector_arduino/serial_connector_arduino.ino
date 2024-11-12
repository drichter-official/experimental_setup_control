// Include the AccelStepper library:
#include <AccelStepper.h>
#include <Adafruit_NeoPixel.h>

// Define stepper motor connections and motor interface type.
// Motor interface type must be set to 1 when using a driver
#define dirPin 2
#define stepPin 3

#define motorInterfaceType 1

#define msc1 8
#define msc2 9
#define msc3 10

// LED Strip Configuration
#define LED_PIN 6
#define LED_COUNT 60
Adafruit_NeoPixel strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Configuration Parameters
#ifndef STEPS_PER_REVOLUTION_BASE
#define STEPS_PER_REVOLUTION_BASE 200
#endif

#ifndef MICRO_STEPPING
#define MICRO_STEPPING 16
#endif

#ifndef MOTOR_MAX_SPEED
#define MOTOR_MAX_SPEED 1600
#endif

#ifndef MOTOR_ACCELERATION
#define MOTOR_ACCELERATION 1600
#endif

long stepsPerRevolutionBase = STEPS_PER_REVOLUTION_BASE;
long microstepping = MICRO_STEPPING;
long maxSpeed = MOTOR_MAX_SPEED;
long acceleration = MOTOR_ACCELERATION;

// Create a new instance of the AccelStepper class:
AccelStepper stepper = AccelStepper(motorInterfaceType, stepPin, dirPin);

void setMicrostepping(int microsteps) {
  if (microsteps == 1) {
    digitalWrite(msc1, LOW);
    digitalWrite(msc2, LOW);
    digitalWrite(msc3, LOW);
  } else if (microsteps == 2) {
    digitalWrite(msc1, HIGH);
    digitalWrite(msc2, LOW);
    digitalWrite(msc3, LOW);
  } else if (microsteps == 4) {
    digitalWrite(msc1, LOW);
    digitalWrite(msc2, HIGH);
    digitalWrite(msc3, LOW);
  } else if (microsteps == 8) {
    digitalWrite(msc1, HIGH);
    digitalWrite(msc2, HIGH);
    digitalWrite(msc3, LOW);
  } else if (microsteps == 16) {
    digitalWrite(msc1, HIGH);
    digitalWrite(msc2, HIGH);
    digitalWrite(msc3, HIGH);
  }
}

void setup() {
  Serial.begin(9600);
  // Initialize microstepping pins:
  pinMode(msc1, OUTPUT);
  pinMode(msc2, OUTPUT);
  pinMode(msc3, OUTPUT);

  // Set microstepping:
  setMicrostepping(microstepping);

  // Set the maximum speed and acceleration in steps per second:
  if (acceleration != 0) {
    stepper.setAcceleration(acceleration * microstepping);
  }
  if (maxSpeed != 0) {
    stepper.setMaxSpeed(maxSpeed * microstepping);
  }

  // Initialize LED strip
  strip.begin();
  strip.clear();
  strip.show();
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    char command = inputString.charAt(0);
    String valueString = inputString.substring(1);
    long value = valueString.toInt();

    // Motor Control Commands
    if (command == 'F') {
      stepper.moveTo(stepper.currentPosition() + value);
      stepper.runToPosition();
    } else if (command == 'B') {
      stepper.moveTo(stepper.currentPosition() - value);
      stepper.runToPosition();
    }

    // LED Strip Control Commands
    else if (command == 'L') { // Turn on entire LED strip with specified brightness (0-255)
      uint8_t brightness = constrain(value, 0, 255);
      strip.setBrightness(brightness);
      for (int i = 0; i <= LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(255, 255, 255)); // Default to white color
      }
      strip.show();
    } else if (command == 'O') { // Turn off entire LED strip
      for (int i = 0; i <= LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(0, 0, 0));
      }
      strip.show();
    } else if (command == 'C') { // Set color of entire LED strip (RRGGBB format)
      long colorValue = strtol(valueString.c_str(), NULL, 16);
      uint8_t r = (colorValue >> 16) & 0xFF;
      uint8_t g = (colorValue >> 8) & 0xFF;
      uint8_t b = colorValue & 0xFF;
      for (int i = 0; i <= LED_COUNT; i++) {
        strip.setPixelColor(i, strip.Color(r, g, b));
      }
      strip.show();
    } else if (command == 'S') { // Set specific LED (format: LED_INDEX,RRGGBB)
      int commaIndex = valueString.indexOf(',');
      if (commaIndex > 0) {
        int ledIndex = valueString.substring(0, commaIndex).toInt();
        long colorValue = strtol(valueString.substring(commaIndex + 1).c_str(), NULL, 16);
        uint8_t r = (colorValue >> 16) & 0xFF;
        uint8_t g = (colorValue >> 8) & 0xFF;
        uint8_t b = colorValue & 0xFF;
        if (ledIndex >= 0 && ledIndex < LED_COUNT) {
          strip.setPixelColor(ledIndex, strip.Color(r, g, b));
          strip.show();
        }
      }
    } else if (command == 'P') { // Turn off specific LED (format: LED_INDEX)
      int ledIndex = valueString.toInt();
      if (ledIndex >= 0 && ledIndex < LED_COUNT) {
        strip.setPixelColor(ledIndex, strip.Color(0, 0, 0));
        strip.show();
      }
    }
  }
}
