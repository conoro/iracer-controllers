#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Conor O'Neill
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simple code to control Arexx Dagu i-racer using MaKey MaKey, Raspberry Pi and Bluetooth

Usage:
  $ sudo iracer_makeymakey_rpi.py <bluetooth_addr_of_iracer>

"""

__author__ = 'cwjoneill@gmail.com (Conor O\'Neill)'

import sys
import select
import tty
import termios
import bluetooth
import time
from evdev import InputDevice, categorize, ecodes, list_devices
import Queue
import threading

queue = Queue.Queue()
decelerate_queue = Queue.Queue()
global current_speed
global current_direction
global sock
global accelerating


class CommandToCar(threading.Thread):
    """Read Command from MakeyMakey and send over Bluetooth to i-racer"""
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        global current_speed
        global current_direction
        global sock
        global accelerating

        while True:
            #wait for start command from main
            control = self.queue.get()

            devices = map(InputDevice, list_devices())

            makey_makey_connected = False
            for dev in devices:
                # print( '%-20s %-32s %s' % (dev.fn, dev.name, dev.phys) )
                if ("Unknown     USB IO Board" in str(dev.name)):
                    makey_makey = str(dev.fn)
                    makey_makey_connected = True

            if (makey_makey_connected == False):
                print "No MaKey MaKey found"

                #signals to queue job is done
                self.queue.task_done()
            
            dev = InputDevice(makey_makey)

            bd_addr = sys.argv[1]
            port = 1
            sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            sock.connect((bd_addr, port))

            prev_event_time = time.time()

            for event in dev.read_loop():
                if event.type == ecodes.EV_KEY:
                    current_event_time = event.timestamp()
                    event_gap = current_event_time - prev_event_time

                    key_pressed = str(categorize(event))
                    # 'down', 'up', or 'hold'?
                    # Event value 1 = button_pressed, Event value 2 = button_held, Event value 0 = button_released
                    if ((event.value == 1) or (event.value == 2)):
                        #cancel any ongoing deceleration
                        accelerating = True
                    else:
                        # button released. Start decelerating
                        accelerating = False 

                    if 'KEY_LEFT' in key_pressed:
                        # 0x5X for left forward. 0x51 very slow. 0x5F fastest
                        # 0x1Y = Straight/Forward, 0x5Y = Left/Forward, 0x6Y = Right/Forward
                        if (current_speed < 0x0F):
                            # 'hold' triggers every .036 seconds. Need slower acceleration than that
                            #  wait until 0.15 secs since we reacted to last event
                            if (event_gap >= 0.15):
                                current_speed += 1
                                prev_event_time = current_event_time
                        
                        # if going forward, forward left or forward right, go forward left
                        if ((current_direction == 0x10) or (current_direction == 0x50) or (current_direction == 0x60)):
                            #print "forward left"
                            current_direction = 0x50
                        # else go backward left    
                        else:
                            #print "backward left"
                            current_direction = 0x70

                    if 'KEY_RIGHT' in key_pressed:
                        # 0x6X for right forward. 0x11 very slow. 0x1F fastest
                        if (current_speed < 0x0F):
                            # 'hold' triggers every .036 seconds. Need slower acceleration than that
                            #  wait until 0.15 secs since we reacted to last event
                            if (event_gap >= 0.15):
                                current_speed += 1
                                prev_event_time = current_event_time
                        
                        # if going forward, forward left or forward right, go forward right
                        if ((current_direction == 0x10) or (current_direction == 0x50) or (current_direction == 0x60)):
                            #print "forward right"
                            current_direction = 0x60
                        # else go backward right    
                        else:
                            #print "backward right"
                            current_direction = 0x80

                    if 'KEY_DOWN' in key_pressed:
                        # 0x2X for straight backward. 0x21 very slow. 0x2F fastest
                        # if going forwards, stop first
                        if ((current_direction == 0x10) or (current_direction == 0x50) or (current_direction == 0x60)):
                            current_speed = 0
                            prev_event_time = current_event_time
                        # if going backwards, keep same speed 
                        if ((current_direction == 0x20) or (current_direction == 0x70) or (current_direction == 0x80)):
                            if (current_speed < 0x0F):
                                # 'hold' triggers every .036 seconds. Need slower acceleration than that
                                #  wait until 0.15 secs since we reacted to last event
                                if (event_gap >= 0.15):
                                    current_speed += 1
                                    prev_event_time = current_event_time
                        #print "backward straight"
                        current_direction = 0x20

                    if 'KEY_UP' in key_pressed:
                        # 0x1X for straight forward. 0x11 very slow. 0x1F fastest
                        # if going backwards, stop first
                        if ((current_direction == 0x20) or (current_direction == 0x70) or (current_direction == 0x80)):
                            current_speed = 0
                            prev_event_time = current_event_time
                        # if going forwards, keep same speed 
                        if ((current_direction == 0x10) or (current_direction == 0x50) or (current_direction == 0x60)):
                            if (current_speed < 0x0F):
                                # 'hold' triggers every .036 seconds. Need slower acceleration than that
                                #  wait until 0.15 secs since we reacted to last event
                                if (event_gap >= 0.15):
                                    current_speed += 1
                                    prev_event_time = current_event_time
                        #print "forward straight"
                        current_direction = 0x10

                    if 'KEY_SPACE' in key_pressed:
                        # using SPACE as the STOP BUTTON
                        current_direction = 0x00
                        current_speed = 0x00

                        #signals to queue job is done
                        self.queue.task_done()

                    # Send Speed/Direction Command over Bluetooth to Car
                    sock.send(chr(current_direction | current_speed))


class DecelerateCar(threading.Thread):
    """With no keys pressed, decelerate the i-racer slowly"""
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global current_speed
        global current_direction
        global sock
        global accelerating

        while True:

            if (accelerating == True):
                time.sleep(0.1)

            else:
            # gradually slow down the car
                if (current_speed > 0):
                    current_speed -= 1 
                    sock.send(chr(current_direction | current_speed))
                    time.sleep(0.3)                    


def main():

    global current_speed
    global current_direction
    global accelerating

    if len(sys.argv) < 2:
        print "usage: sudo iracer_makeymakey_rpi.py <addr>"
        print "   use hcitool scan to get bluetooth address of Dagu i-racer"
        sys.exit(2)

    #Set Car Speed and Direction
    current_speed = 0x00
    current_direction = 0x10
    accelerating = True

    #Just one MakeyMakey->iRacer thread. Pass it the queue instance 
    t = CommandToCar(queue)
    t.setDaemon(True)
    t.start()

    d = DecelerateCar()
    d.setDaemon(True)
    d.start()

    #Start Scanning the MakeyMakey for Key Presses   
    queue.put("start")

    #wait on the queue until stop key pressed and then exit     
    queue.join()


main()
