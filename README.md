i-Racer + MaKey MaKey + Raspberry Pi
------------------------------------
Simple code to control Arexx Dagu i-racer using MaKey MaKey, Raspberry Pi and Bluetooth. 

Description
-----------
This code enables you to use any vaguely conductive materials connected to a MaKey MaKey to send keystrokes to a Raspberry Pi and onwards over Bluetooth to the Arexx Dagu i-Racer Bluetooth RC car. The code should run unmodified on most recent versions of Ubuntu and Debian.

Lots more details on http://conoroneill.net/makey-makey-raspberry-pi-iracer-bluetooth-cheese-controlled-car-ccc/

Pre-Requisites
--------------

```bash
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python-pip python-dev build-essential
sudo apt-get install bluetooth bluez python-bluez bluez-hcidump
sudo pip install evdev
```

Now you need to work around a nasty bug in Debian and Ubuntu.
```bash
sudo nano /etc/bluetooth/main.conf
```

add this line to it:
```bash
DisablePlugins = pnat
```

Setup
-----
Power up Raspberry Pi with MaKey MaKey on powered USB hub but with Bluetooth dongle not plugged in.

Now plug in the Bluetooth dongle into one of the Raspberry Pi's USB ports, not on the USB Hub. Power up the i-racer and run:

```bash
hcitool dev
```

It should detect your dongle and report its MAC address. If it does, then run:

```bash
hcitool scan
```

This should find the i-racer as a Dagu Car. Note its MAC address and then pair to it by running:

```bash
sudo bluez-simple-agent hci0 00:12:05:09:94:26
```

where you replace 00:12:05:09:94:26 with the MAC address of your car. The PIN is either 1234 or 0000. Note it must be run as sudo or you'll get bluez errors.

Running
-------
run the code with:

```bash
sudo iracer_makeymakey_rpi.py <bluetooth_addr_of_iracer>
```

What Next?
----------
Next up is probably Wiimote control and then a slight chance of doing a PhoneGap mobile app. I will probably try direct Arduino control using a serial bluetooth add-on too at some stage.

Changelog
=========

2013/01/03
----------
First rough version. Not very responsive but more controllable than the Android App.

