#include <AccelStepper.h>
#include <PID_v1.h>

AccelStepper stepper1(AccelStepper::DRIVER, 2, 5);
long BallPos = 0;

double Setpoint ;
double Input ;
double Output ;
double Kp=0.1, Ki=0, Kd=0.01;

PID myPID(&Input, &Output, &Setpoint, Kp, Ki, Kd, DIRECT);

void setup() {
  Serial.begin(115200);
  while(!Serial) {}

  Setpoint = 0;
  myPID.SetMode(AUTOMATIC);
  myPID.SetTunings(Kp, Ki, Kd);
  myPID.SetOutputLimits(-720,720);
  myPID.SetSampleTime(10);
  
  stepper1.setMaxSpeed(16000);
  stepper1.setAcceleration(24000);
  stepper1.setCurrentPosition(0);
}

void loop() {
  // Handle serial
  if (Serial.available() > 0) {
    String message = Serial.readStringUntil('\n');
    BallPos = message.toInt();
    Input = BallPos;
    myPID.Compute();
    if (Output != 0) {
      stepper1.moveTo(Output);
    }
  }
  // Keep motor running freely
  stepper1.run();
}

