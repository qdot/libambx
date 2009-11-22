#################################################################
# python amBX controller object
# By Kyle Machulis <kyle@nonpolynomial.com>
# http://www.nonpolynomial.com
#
# Distributed as part of the libambx project
#
# Website: http://qdot.github.com/libambx
# Repo: http://www.github.com/qdot/libambx
#
# Licensed under the BSD License, as follows
#
# Copyright (c) 2009, Kyle Machulis/Nonpolynomial Labs
# All rights reserved.
#
# Redistribution and use in source and binary forms, 
# with or without modification, are permitted provided 
# that the following conditions are met:
#
#    * Redistributions of source code must retain the 
#      above copyright notice, this list of conditions 
#      and the following disclaimer.
#    * Redistributions in binary form must reproduce the 
#      above copyright notice, this list of conditions and 
#      the following disclaimer in the documentation and/or 
#      other materials provided with the distribution.
#    * Neither the name of the Nonpolynomial Labs nor the names 
#      of its contributors may be used to endorse or promote 
#      products derived from this software without specific 
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND 
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, 
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, 
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#################################################################

import sys, os

#Requires PyUSB
#http://pyusb.berlios.de/
import usb

class ambx:
    
    #Device as retreived from the bus listing
    ambx_device = None
    #Handle to access the device with
    ambx_handle = None
    #Internal command index holder. Counts to 0xf, rolls over, starts again
    command_index = 0
    #Set to true to print out debug messages
    debug = False

    #VID/PID for amBX Controller
    AMBX_VENDOR_ID = 0x0471
    AMBX_PRODUCT_ID = 0x083F
    
    #Conveinence strings for device addresses
    LEFT_SP_LIGHT = 0x0B
    RIGHT_SP_LIGHT = 0x1B
    LEFT_WW_LIGHT = 0x2B
    CENTER_WW_LIGHT = 0x3B
    RIGHT_WW_LIGHT = 0x4B
    LEFT_FAN = 0x5B
    RIGHT_FAN = 0x6B
    RUMBLE = 0x7B

    #Conveinence strings for device commands
    cmd = { 'SetLightColor'     : 0x03, \
                'SetListWithDelay'  : 0x72, \
                'SetFanSpeed'       : 0x01  \
                } 
        
    #Conveinence strings for device endpoints
    ep = { 'in'  : 0x81, \
               'out' : 0x02, \
               'pnp' : 0x83 \
               }

    #Constructor
    def __init__(self):
        return

    #Function for flattening embedded lists
    #found at http://www.daniel-lemire.com/blog/archives/2006/05/10/flattening-lists-in-python/
    def flattenList(self, l):
        """ Given a list of embedded lists, flattens them into a 
        single list 
        
        Returns flattened list.
        """
        return reduce(lambda a, b: isinstance(b, (list, tuple)) and a+list(b) or a.append(b) or a, l, [])

    def open(self, index = 0):
        """ Given an index, opens the related ambx device. The index refers
        to the position of the device on the USB bus. Index 0 is default, 
        and will open the first device found.

        Returns True if open successful, False otherwise.
        """
        self.ambx_device = usb.core.find(idVendor = self.AMBX_VENDOR_ID, 
                                               idProduct = self.AMBX_PRODUCT_ID)
        if self.ambx_device is None:
            return False
        self.ambx_device.set_configuration(1)
        #self.ambx_device.claim_interface(0)
        return True

    def close(self):
        """Closes the amBX device currently held by the object, 
        if it is open."""
        if self.ambx_device is not None:
            self.ambx_device = None

    def write(self, command):
        """Given a list of raw bytes, writes them to the out endpoint of the
        ambx controller.

        Returns total number of bytes written.
        """
        if self.debug:
            [sys.stdout.write("0x%.2x " % ord(x)) for x in command]        
            print
        return self.ambx_device.write(self.ep['out'], map(ord,command), 0, 1)

    def read(self, size=64):
        """Reads in the requested amount of bytes
        from the in endpoint of the ambx device.
        
        Returns list of bytes read.
        """
        status = self.ambx_device.read(self.ep['in'], size, 0, 1)

    def compileCommand(self, address, command, parameters):
        """Given an address (1 byte), command (1 byte), and parameter (list),
        compiles them into a single array of bytes to send to the device. Also
        manages the incrementing of the command sequence value."""
        if self.debug:
            print 'Building Command: %x %x %x %s' % ((((((self.command_index % 16)) << 4) | 1)), address, self.cmd[command], parameters)
        compiled_command = [(((self.command_index % 16)) << 4) | 1, 
                            address, self.cmd[command]]
        self.command_index += 1        
        compiled_command.extend(self.flattenList(parameters))
        return map(chr, compiled_command)

    def expandDelay(self, delay):
        """Given a delay value, expands it into the 2 byte list required for
        command consumption (i.e. a list consisting of the upper and lower 
        bytes)"""
        if delay < 255:
            return [0, delay]
        return [(delay & 0xff00) >> 8, delay & 0xff] 

    def setLightColor(self, light, color):
        """Given a light address and a color (list of 3 integers, in R, G, B
        order), sets the light to that color"""
        self.write(self.compileCommand(light, 'SetLightColor', color))
        return

    def setLightColorList(self, light, delay, color_list):
        """Given 
        
        - a light address
        - a delay value, in milliseconds 
        - a list of up to 16 colors 
        -- one list of 3 integers per color, in R, G, B order

        replays the list at that address, holding at each value for the 
        specified delay time"""
        self.write(self.compileCommand(light, 'SetListWithDelay',[self.expandDelay(delay), self.flattenList(color_list)]))
        return
        
    def setFanSpeed(self, fan, speed):
        """Given a fan address and a speed, sets the fan to that speed"""
        self.write(self.compileCommand(fan, 'SetFanSpeed', [speed]))
        return

    def setFanSpeedList(self, fan, delay, speed_list):
        """Given 

        - a fan address 
        - a delay value, in milliseconds
        - a list of up to 48 speeds
        -- speed is just a bare integer, so a single list of up to 48 integers

        replays the list at that address, holding at each value for the 
        specified delay time"""
        self.write(self.compileCommand(fan, 'SetListWithDelay', [self.expandDelay(delay), speed_list]))
        return

    def setRumbleSpeed(self, rumble, speed):
        """Given a rumble address and a speed (list of two values, for right and
        left rumble motors), sets the rumble strip to that speed"""
        return

    def setRumbleSpeedList(self, rumble, delay, speed_list):
        """Given 

        - a rumble address
        - a delay value
        - a list of up to 24 speeds
        -- one list of 2 integers per speed, for left/right motor

        replays the list at that address, holding at each value for the 
        specified delay time
        """
        self.write(self.compileCommand(rumble, cmd['SetListWithDelay'], [self.expandDelay(delay), speed_list]))
        return
    
def main(argv=None):
    ambx_device = ambx()
    ambx_device.debug = True
    if ambx_device.open() is False:
        print "No ambx device connected"
        return

    #Some things you can do
    #ambx_device.setFanSpeed(ambx.LEFT_FAN, 0xFF)

    ambx_device.setLightColor(ambx.LEFT_WW_LIGHT, [0x70, 0x50, 0xa0])
    ambx_device.setLightColor(ambx.CENTER_WW_LIGHT, [0x70, 0x50, 0xa0])
    ambx_device.setLightColor(ambx.RIGHT_WW_LIGHT, [0x70, 0x50, 0xa0])
    ambx_device.setLightColor(ambx.RIGHT_SP_LIGHT, [0x70, 0x50, 0xa0])

    ambx_device.setLightColor(ambx.LEFT_SP_LIGHT, [0x70, 0x50, 0xa0])
    #ambx_device.setLightColorList(ambx.LEFT_SP_LIGHT, 100, [[x*4, x*1, x*8] for x in range(16) ])
    #ambx_device.setLightColorList(ambx.RIGHT_SP_LIGHT, 100, [[x*4, x*1, x*8] for x in range(16) ])

    #ambx_device.setLightColorList(ambx.CENTER_WW_LIGHT, 100, [[x*4, x*1, x*6] for x in range(16) ])
    #ambx_device.setLightColorList(ambx.LEFT_WW_LIGHT, 100, [[x*4, x*1, x*6] for x in range(16) ])
    #ambx_device.setLightColorList(ambx.RIGHT_WW_LIGHT, 100, [[x*4, x*1, x*6] for x in range(16) ])
    #ambx_device.setFanSpeedList(ambx.LEFT_FAN, 1000, range(0, 255, 255/48))
    #ambx_device.setFanSpeed(ambx.LEFT_FAN, 0)
    ambx_device.close()
    
if __name__ == "__main__":
        
    sys.exit(main())
