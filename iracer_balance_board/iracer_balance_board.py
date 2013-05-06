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

"""Simple code to control Arexx Dagu i-racer using Raspberry Pi and Wii Balance Board

Usage:
  $ python iracer_balance_board.py

"""

__author__ = 'cwjoneill@gmail.com (Conor O\'Neill)'

import cwiid
import sys
import bluetooth
import time
import math

global sock
global wiimote
 
def main():


    print 'Press Red Sync Button in Battery Compartment of Balance Board...'

    # Wii Balance Board
    rpt_mode = 0

	# Change the number below to the Bluetooth MAC address of your Wii Balance Board
    # You get that by pressing red sync button in battery compartment and then running
    # hcitool scan	
    wiimote = cwiid.Wiimote("00:1E:35:C0:E3:FD")

    rpt_mode ^= cwiid.RPT_EXT
    wiimote.rpt_mode = rpt_mode


    # i-racer 
	# Change the number below to the Bluetooth MAC address of your i-racer
    # You get that by turning on the i-racer and and then running
    # hcitool scan	
    bd_addr = "00:12:05:09:95:33"
    port = 1
    sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
    sock.connect((bd_addr, port))

    # Probably a good idea to have recently calibrated your Balance Board on your Wii
    balance_calibration = wiimote.get_balance_cal()
    # print balance_calibration
    right_top_cal = balance_calibration[0][0]
    right_bottom_cal = balance_calibration[1][0]
    left_top_cal = balance_calibration[2][0]
    left_bottom_cal = balance_calibration[3][0]

    while True:
	    # Quite a slow refresh rate. Feel free to reduce this time (it's in seconds)
        time.sleep(0.5)
        wiimote.request_status()

        right_top = wiimote.state['balance']['right_top'] - right_top_cal
        right_bottom =  wiimote.state['balance']['right_bottom'] - right_bottom_cal
        left_top =  wiimote.state['balance']['left_top'] - left_top_cal
        left_bottom = wiimote.state['balance']['left_bottom'] - left_bottom_cal

        LEFT_RIGHT_MULTIPLIER = 1.2
        FRONT_BACK_MULTIPLIER = 1.2

        lean = "Indeterminate"
        
        # No one on the Balance Board yet		
        if ((right_bottom < 100) and (right_top < 100) and (left_bottom < 100) and (left_top < 100)):
            lean = "Stop"
			
		    # Leaning towards the front left of the Balance Board	
        elif (((right_top == 0) or (abs(left_top/float(right_top)) >= LEFT_RIGHT_MULTIPLIER)) and
            ((left_bottom == 0) or (abs(left_top/float(left_bottom)) >= FRONT_BACK_MULTIPLIER))):
            lean = "Left Top"

        # Leaning towards the front right of the Balance Board	
        elif (((left_top == 0)  or (abs(right_top/float(left_top)) >= LEFT_RIGHT_MULTIPLIER)) and
              ((right_bottom == 0) or (abs(right_top/float(right_bottom)) >= FRONT_BACK_MULTIPLIER))):
            lean = "Right Top"

		    # Leaning towards the back left of the Balance Board	
        elif (((right_bottom == 0) or (abs(left_bottom/float(right_bottom)) >= LEFT_RIGHT_MULTIPLIER)) and
              ((left_top == 0) or (abs(left_bottom/float(left_top)) >= FRONT_BACK_MULTIPLIER))):
            lean = "Left Bottom"

		    # Leaning towards the back right of the Balance Board	
        elif (((right_top == 0) or (abs(right_bottom/float(right_top)) >= FRONT_BACK_MULTIPLIER)) and
              ((left_bottom == 0) or (abs(right_bottom/float(left_bottom)) >= LEFT_RIGHT_MULTIPLIER))):
            lean = "Right Bottom"

		    # Leaning towards the front middle of the Balance Board	
        elif (((right_bottom == 0) or (abs(right_top/float(right_bottom)) >= FRONT_BACK_MULTIPLIER)) and
              ((left_bottom == 0) or (abs(left_top/float(left_bottom)) >= FRONT_BACK_MULTIPLIER)) and
              ((right_top == 0) or (abs(left_top/float(right_top)) < LEFT_RIGHT_MULTIPLIER))):
            lean = "Middle Top"

		    # Leaning towards the back middle of the Balance Board	
        elif (((right_top == 0) or (abs(right_bottom/float(right_top)) >= FRONT_BACK_MULTIPLIER)) and
              ((left_top == 0) or (abs(left_bottom/float(left_top)) >= FRONT_BACK_MULTIPLIER)) and
              ((right_bottom == 0) or (abs(left_bottom/float(right_bottom)) < LEFT_RIGHT_MULTIPLIER))):
            lean = "Middle Bottom"

        # Anywhere in the middle of the board considered to be Stop			
        elif (((right_bottom == 0) or (abs(right_top/float(right_bottom)) < FRONT_BACK_MULTIPLIER)) and
              ((left_bottom == 0) or (abs(left_top/float(left_bottom)) < FRONT_BACK_MULTIPLIER))):
            lean = "Stop"
        print lean
        
        #print ('Balance Report: right_top=%s right_bottom=%s ' + \
        #       'left_top=%s left_bottom=%s') % \
        #      (right_top, right_bottom, left_top, left_bottom)
        if ((right_bottom != 0) and (right_top != 0) and (left_bottom != 0) and (left_top != 0)):
            print ('RT/RB = %.2f LT/LB = %.2f RT/LT = %.2f RB/LB = %.2f') % \
                  (abs(right_top/float(right_bottom)), abs(left_top/float(left_bottom)), abs(right_top/float(left_top)), abs(right_bottom/float(left_bottom))) 	  

        if (lean == "Left Top"):
        #    # 0x5X for left forward. 0x51 very slow. 0x5F fastest
            sock.send('\x5A')
        if (lean == "Right Top"):
        #    # 0x6X for right forward. 0x11 very slow. 0x1F fastest
            sock.send('\x6A')
        if (lean == "Middle Top"):
        #    # 0x1X for straight forward. 0x11 very slow. 0x1F fastest
            sock.send('\x1A')
        if (lean == "Left Bottom"):
        #    # 0x7X for left backwards. 0x71 very slow. 0x7F fastest
            sock.send('\x7A')
        if (lean == "Right Bottom"):
        #    # 0x8X for right backwards. 0x81 very slow. 0x8F fastest
            sock.send('\x8A')
        if (lean == "Middle Bottom"):
        #    # 0x2X for straight backward. 0x21 very slow. 0x2F fastest
            sock.send('\x2A')
        if (lean == "Stop"):
        #    #stop
            sock.send('\x00')

main()
