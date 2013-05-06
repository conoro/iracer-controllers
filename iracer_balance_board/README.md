i-Racer + Wii Balance Board + Raspberry Pi
------------------------------------
Simple code to control Arexx Dagu i-racer over Bluetooth using a Raspberry Pi and a Wii Balance Board

Description
-----------
This code enables you to use a cheap generic USB Bluetooth dongle on a Raspberry Pi to communicate with both a Wii Balance Board and Arexx Dagu i-Racer Bluetooth RC. You control the i-racer by leaning on the Balance Board.

Lots more details on http://conoroneill.net/controlling-an-i-racer-rc-car-using-a-wii-balance-board-and-raspberry_pi including instructions on replacing the standard cwiid libraries on the Raspberry Pi with ones that recognise the Balance Board properly.

Pre-Requisites
--------------
* Arexx Dagu i-racer
* Raspberry Pi
* Cheap Chinese Bluetooth Adapter
* Wii Balance Board


Setup
-----
No physical setup required. Only major drawback is that you have to press the red sync button in the battery compartment of the Wii Balance Board every time you run the code. As this is not necessary on the Wii, there should be a way around this.

Running
-------
Edit the code to change the Bluetooth MAC addresses to your Balance Board and your i-racer. then just do python iracer_balance_board.py

Changelog
=========

2013/05/06
----------
First version. Works reasonably well but "zone" handling quite crude and doesn't cover all positions on the Balance Board. Could probably be improved a lot.

