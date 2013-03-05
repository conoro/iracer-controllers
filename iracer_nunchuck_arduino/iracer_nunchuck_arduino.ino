/*
  Portions of code Copyright Chris Samuelson 2012 See http://cu.rious.org/make/hc-05-bluetooth-with-arduino/
  Portions of code Copyright Chad Phillips 2007 See http://www.windmeadow.com/node/42

  Remainder of code Copyright (C) 2013 Conor O'Neill

  Conor O'Neill's code is Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/


/* Nunchuck Connections:
 On Arduino Nano connect Nunchuck Pins as follows:
 Red = 5V POWER = Nano Pin 5V
 White = GND = Nano Pin GND
 Green = SDA = Nano Analogue Pin A4
 Yellow = SCL = Nano Analogue Pin A5
*/

#include <SoftwareSerial.h> //Software Serial Port

#include <Wire.h>

// HC=05 Bluetooth Serial Module Connections:
#define Reset 5 //Connect Digital Pin 5 of Nano to VCC on HC-05
#define RxD 6   //Connect Digital Pin 6 of Nano to TXD on HC-05
#define TxD 7   //Connect Digital Pin 7 of Nano to RXD on HC-05
#define PIO11 8 //Connect Digital Pin 8 of Nano to KEY on HC-05
#define Led 13

// Find out the Bluetooth MAC address of your i-racer (using a phone or PC) and put it here in this format
char Bluetooth_Address[] = "0012,05,099533"; 

uint8_t outbuf[6];		// array to store arduino output
int cnt = 0;
int ledPin = 13;
byte bt_command = 0x00;
 
SoftwareSerial blueToothSerial(RxD,TxD);
 
void setup()
{
 // Serial Port
 Serial.begin(19200);
 
 // Nunchuck
 Wire.begin ();		// join i2c bus with address 0x52
 nunchuck_init (); // send the initilization handshake

 // Bluetooth
 pinMode(RxD, INPUT);
 pinMode(TxD, OUTPUT);
 pinMode(Led, OUTPUT);
 pinMode(PIO11, OUTPUT);
 digitalWrite(PIO11, HIGH);
 pinMode(Reset, OUTPUT);
 digitalWrite(Reset, LOW);
 setupBlueToothConnection();
}
 
void loop()
{

  Wire.requestFrom (0x52, 6);	// request data from nunchuck
  while (Wire.available ())
    {
      outbuf[cnt] = nunchuk_decode_byte (Wire.read ());	// receive byte as an integer
      cnt++;
    }

  // If we have received the 6 bytes, then go print them
  if (cnt >= 5)
    {
      bt_command = nunchuck_evaluate ();
      blueToothSerial.write((byte)bt_command);
    }

  cnt = 0;
  send_zero (); // send the request for next bytes
  delay (100);
}

byte nunchuck_evaluate ()
{
  int joy_x_axis = outbuf[0];
  int joy_y_axis = outbuf[1];
  int accel_x_axis = outbuf[2] * 2 * 2; 
  int accel_y_axis = outbuf[3] * 2 * 2;
  int accel_z_axis = outbuf[4] * 2 * 2;

  int z_button = 0;
  int c_button = 0;

  float normalised_joystick_x;
  float normalised_joystick_y;
  float normalised_speed;
  byte current_speed; 
  byte current_direction; 
  float angle;

 // byte outbuf[5] contains bits for z and c buttons
 // it also contains the least significant bits for the accelerometer data
 // so we have to check each bit of byte outbuf[5]
  if ((outbuf[5] >> 0) & 1)
    {
      z_button = 1;
    }
  if ((outbuf[5] >> 1) & 1)
    {
      c_button = 1;
    }

  if ((outbuf[5] >> 2) & 1)
    {
      accel_x_axis += 2;
    }
  if ((outbuf[5] >> 3) & 1)
    {
      accel_x_axis += 1;
    }

  if ((outbuf[5] >> 4) & 1)
    {
      accel_y_axis += 2;
    }
  if ((outbuf[5] >> 5) & 1)
    {
      accel_y_axis += 1;
    }

  if ((outbuf[5] >> 6) & 1)
    {
      accel_z_axis += 2;
    }
  if ((outbuf[5] >> 7) & 1)
    {
      accel_z_axis += 1;
    }

/*
 I am treating Nunchuck movement as 6 Segments of 60 degrees each:
 Fwd, Fwd-R, Bck-R, Bck, Bck-L, Fwd-L

 Fwd-R: Unit Circle (x,y): (1 -> Cos 60, 0 -> Sin 60)
 Fwd: Unit Circle (x,y): (Cos 60 - Cos 120, Sin 60 -> Sin 120)
 Fwd-L: Unit Circle (x,y): (Cos 120 -> -1, Sin 120 -> 0)
 Bck-L: Unit Circle (x,y): (-1 -> Cos 240, 0 -> Sin 240)
 Bck: Unit Circle (x,y): (Cos 240 -> Cos 300, Sin 240 -> Sin 300)
 Bck-R: Unit Circle (x,y): (Cos 300 -> 1, Sin 300 -> 0)

 Nunchuck Approx Centre (120, 120) (May need to tweak)
 Nunchuck Approx Range +/- 95

 Normalise and calculate angle between vectors
 Cos (angle) =(u1*v1 + u2*v2)/(sqrt(u1^2 + u2^2)* sqrt(v1^2 + v2^2))
 We are always comparing to (1,0) so equation becomes
 angle = arccos(v1/sqrt(v1^2 + v2^2))
 Then add 180 to angle if v2 < 0
*/

  normalised_joystick_x = ((float)joy_x_axis - 132)/100; 
  if (normalised_joystick_x > 1){
      normalised_joystick_x = 1;
  }
  else if (normalised_joystick_x < -1){
	normalised_joystick_x = -1;
  }
  normalised_joystick_y = ((float)joy_y_axis - 115)/100;
  if (normalised_joystick_y > 1){
	normalised_joystick_y = 1;
  }
  else if (normalised_joystick_y < -1){
	normalised_joystick_y = -1;
  }
  normalised_speed = sqrt(normalised_joystick_x*normalised_joystick_x + normalised_joystick_y*normalised_joystick_y);
  if (normalised_speed > 1){
	normalised_speed = 1;
  }

  // Radians to Degrees
  angle = (acos(normalised_joystick_x/sqrt(normalised_joystick_x*normalised_joystick_x + normalised_joystick_y*normalised_joystick_y))) * 57296 / 1000;

  // Probably need to have some jitter compensation here
  if (normalised_joystick_y < 0){
    angle += 180;
  }

  //max dagu speed is 0x0f
  current_speed = round(normalised_speed*15);
			
  // Change speed/direction based on Nunchuck inputs
  if (angle  < 60){
    // forward right
    // 0x6Y = Right/Forward
    current_direction = 0x60;
  }

  if ((angle >= 60) and (angle < 120)){
    // forward
    // 0x1Y = Straight/Forward
    current_direction = 0x10;
  }

  if ((angle >= 120) and (angle < 180)){
    // forward left
    // 0x5X for left forward. 0x51 very slow. 0x5F fastest
    current_direction = 0x50;
  }

  if ((angle >= 180) and (angle < 240)){
    // backward left
    // 0x7Y Left / Backward 0xX7 Cruising
    current_direction = 0x70;
  }

  if ((angle >= 240) and (angle < 300)){
    // backward
    // 0x2X for straight backward. 0x21 very slow. 0x2F fastest
    current_direction = 0x20;
  }

  if (angle >= 300){
    // backward right
    // 0x8Y Right / Backward
    current_direction = 0x80;
  }
  
  if (z_button == 0){
    // stop
    current_direction = 0x00;
    current_speed = 0x00;
  }
  
  //Send Speed/Direction Command over Bluetooth to Car
  return(current_direction | current_speed);
}

 
void setupBlueToothConnection()
{
 char Command[20];
 enterATMode();
 sendATCommand();
 sendATCommand("UART=38400,0,0");
 sendATCommand("ROLE=1");
 sendATCommand("PSWD=1234");
 sprintf(Command, "PAIR=%s", Bluetooth_Address);
 sendATCommand(Command);
 sprintf(Command, "BIND=%s", Bluetooth_Address);
 sendATCommand(Command);
 sendATCommand("CMODE=0");
 enterComMode();
}
 
void resetBT()
{
 digitalWrite(Reset, LOW);
 delay(2000);
 digitalWrite(Reset, HIGH);
}
 
void enterComMode()
{
 blueToothSerial.flush();
 delay(500);
 digitalWrite(PIO11, LOW);
 resetBT();
 delay(500);
 blueToothSerial.begin(38400);
}
 
void enterATMode()
{
 blueToothSerial.flush();
 delay(500);
 digitalWrite(PIO11, HIGH);
 resetBT();
 delay(500);
 blueToothSerial.begin(38400);
 
}
 
void sendATCommand(char *command)
{
 blueToothSerial.print("AT");
 if(strlen(command) > 1){
 blueToothSerial.print("+");
 blueToothSerial.print(command);
 delay(100);
 }
 blueToothSerial.print("\r\n");
}
 
void sendATCommand()
{
 blueToothSerial.print("AT\r\n");
 delay(100);
}


void nunchuck_init ()
{
  Wire.beginTransmission (0x52);	// transmit to device 0x52
  Wire.write (0x40);		// sends memory address
  Wire.write (0x00);		// sends sent a zero.  
  Wire.endTransmission ();	// stop transmitting
}

void send_zero ()
{
  Wire.beginTransmission (0x52);	// transmit to device 0x52
  Wire.write (0x00);		// sends one byte
  Wire.endTransmission ();	// stop transmitting
}

// Encode data to format that most wiimote drivers accept
// only needed if you use one of the regular wiimote drivers
char nunchuk_decode_byte (char x)
{
  x = (x ^ 0x17) + 0x17;
  return x;
}


