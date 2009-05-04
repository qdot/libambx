from optparse import OptionParser
import sys
import usb

class ambx:
    #device variables
    ambx_device = None
    ambx_handle = None
    command_index = 0
    debug = False

    AMBX_VENDOR_ID = 0x0471
    AMBX_PRODUCT_ID = 0x083F
    
    #device addresses
    LEFT_SP_LIGHT = 0x0B
    RIGHT_SP_LIGHT = 0x1B
    LEFT_WW_LIGHT = 0x2B
    CENTER_WW_LIGHT = 0x3B
    RIGHT_WW_LIGHT = 0x4B
    LEFT_FAN = 0x5B
    RIGHT_FAN = 0x6B
    RUMBLE = 0x7B

    #command indexes
    cmd = { 'SetLightColor'     : 0x03, \
                'SetListWithDelay'  : 0x72, \
                'SetFanSpeed'       : 0x01  \
                } 
        
    #endpoints
    ep = { 'in'  : 0x81, \
               'out' : 0x02, \
               'pnp' : 0x83 \
               }

        
    def __init__(self):
        return

    #found at http://www.daniel-lemire.com/blog/archives/2006/05/10/flattening-lists-in-python/
    def flattenList(self, l):
        return reduce(lambda a, b: isinstance(b, (list, tuple)) and a+list(b) or a.append(b) or a, l, [])

    def open(self, index = 0):
        device_count = 0
        for bus in usb.busses():
            devices = bus.devices
            for dev in devices:
                if dev.idVendor == self.AMBX_VENDOR_ID and dev.idProduct == self.AMBX_PRODUCT_ID :
                    if device_count == index:
                        self.ambx_device = dev
                        break;
                    device_count += 1            
        if self.ambx_device is None:
            return False
        self.ambx_handle = self.ambx_device.open()
        self.ambx_handle.setConfiguration(1)
        self.ambx_handle.claimInterface(0)
        return True

    def close(self):
        if self.ambx_handle is not None:
            self.ambx_handle.releaseInterface() 
            self.ambx_handle = None

    def write(self, command):
        if self.debug:
            [sys.stdout.write("0x%.2x " % ord(x)) for x in command]        
            print
        self.ambx_handle.bulkWrite(self.ep['out'], command, 1)

    def read(self, status, size=64):
        status = self.ambx_handle.bulkRead(self.ep['in'], size, 1)

    def compileCommand(self, address, command, parameters):
        if self.debug:
            print 'Building Command: %x %x %x %s' % ((((((self.command_index % 16)) << 4) | 1)), address, self.cmd[command], parameters)
        compiled_command = [(((self.command_index % 16)) << 4) | 1, address, self.cmd[command]]
        self.command_index += 1        
        compiled_command.extend(self.flattenList(parameters))
        return map(chr, compiled_command)

    def expandDelay(self, delay):
        if delay < 255:
            return [0, delay]
        return [(delay & 0xff00) >> 8, delay & 0xff] 

    def setLightColor(self, light, color):
        self.write(self.compileCommand(light, 'SetLightColor', color))
        return

    def setLightColorList(self, light, delay, color_list):
        self.write(self.compileCommand(light, 'SetListWithDelay', [self.expandDelay(delay), self.flattenList(color_list)]))
        return
        
    def setFanSpeed(self, fan, speed):
        self.write(self.compileCommand(fan, 'SetFanSpeed', [speed]))
        return

    def setFanSpeedList(self, fan, delay, speed_list):
        self.write(self.compileCommand(fan, 'SetListWithDelay', [self.expandDelay(delay), speed_list]))
        return

    def setRumbleSpeed(self, rumble, speed):
        return

    def setRumbleSpeedList(self, rumble, delay, speed_list):
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
    #ambx_device.setLightColor(ambx.LEFT_WW_LIGHT, [0, 0, 0xFF])
    #ambx_device.setLightColor(ambx.CENTER_WW_LIGHT, [0, 0xFF, 0])
    #ambx_device.setLightColor(ambx.RIGHT_WW_LIGHT, [0xFF, 0, 0])
    #ambx_device.setLightColorList(ambx.LEFT_WW_LIGHT, 100, [[0, 0, x * 10] for x in range(16) ])
    #ambx_device.setFanSpeedList(ambx.LEFT_FAN, 1000, range(0, 255, 255/48))
    #ambx_device.setFanSpeed(ambx.LEFT_FAN, 0)
    ambx_device.close()
    
if __name__ == "__main__":
        
    sys.exit(main())
