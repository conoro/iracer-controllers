i-Racer + MaKey MaKey + Raspberry Pi
------------------------------------
Simple code to control Arexx Dagu i-racer over Bluetooth using Arduino Nano, HC-05 Bluetooth module and Wii Nunchuck

Description
-----------
This code enables you to use the HC-05 Bluetooth Master Mode serial module with an Arduino to communicate with an Arexx Dagu i-Racer Bluetooth RC car and direct it with a Wii Nunchuck.

Lots more details on http://conoroneill.net/using-a-wii-nunchuck-instead-of-cheese-to-control-i-racer-rc-car-raspberry_pi-and-arduino including test code to do the same with a Raspberry Pi and Python.

Pre-Requisites
--------------
* Arexx Dagu i-racer
* Arduino (I used both Nano and Uno)
* HC-05 Bluetooth Module
* Wii Nunchuck
* Wii Nunchuck connection adapter (Optional)

Setup
-----
* On Arduino Nano, connect Nunchuck wires as follows:
    * Red = 5V POWER = Nano Pin 5V
    * White = GND = Nano Pin GND
    * Green = SDA = Nano Analogue Pin A4
    * Yellow = SCL = Nano Analogue Pin A5
* On Arduino Nano, connect HC-05 pins as follows:
    * Connect Digital Pin 5 of Nano to VCC on HC-05
    * Digital Pin 6 of Nano to TXD on HC-05
    * Connect Digital Pin 7 of Nano to RXD on HC-05
    * Connect Digital Pin 8 of Nano to KEY on HC-05
* Find out the Bluetooth MAC address of your i-racer using a phone or PC. Edit the code and change the MAC address there.

Running
-------
Just select Nano with ATMega328 in the Arduino IDE and send the code to the Nano.

Changelog
=========

2013/03/05
----------
First version. Works extremely well but tuned specifically for the old Wii Nunchuck I tested with and which seems to have reduced range of motion.

