// Include the AccelStepper library:
#include "AccelStepper.h"

// Define stepper motor connections and motor interface type.
// Motor interface type must be set to 1 when using a driver
#define dirPin 2
#define stepPin 3

#define motorInterfaceType 1

#define msc1 8
#define msc2 9
#define msc3 10

// Configuration Parameters
#ifndef STEPS_PER_REVOLUTION_BASE
#define STEPS_PER_REVOLUTION_BASE 200
#endif

#ifndef MICROSTEPPING
#define MICROSTEPPING 16
#endif

#ifndef MAX_SPEED
#define MAX_SPEED 1600
#endif

#ifndef ACCELERATION
#define ACCELERATION 0
#endif

int stepsPerRevolutionBase = STEPS_PER_REVOLUTION_BASE;
int microstepping = MICROSTEPPING;
int maxSpeed = MAX_SPEED;
int acceleration = ACCELERATION;

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
}

void loop() {
  if (Serial.available() > 0) {
    String inputString = Serial.readStringUntil('\n');
    char command = inputString.charAt(0);
    String valueString = inputString.substring(1);
    int value = valueString.toInt();

    // Motor Control Commands
    if (command == 'F') {
      stepper.moveTo(stepper.currentPosition() + value);
      stepper.runToPosition();
    } else if (command == 'B') {
      stepper.moveTo(stepper.currentPosition() - value);
      stepper.runToPosition();
    }
  }
}
