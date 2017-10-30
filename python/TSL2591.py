"""
Class to talk to the TSL2591 light sensor.
"""
import smbus

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

class TSL2591(object):
    def __init__(self, bus=None):
        if bus==None: self._bus=smbus.SMBus(1)
        else: self._bus=bus
        self._address=0x29
        
        # Make sure that I can correctly read the device ID (should always be 0x50)
        if( self._readRegister(0x12)!=0x50 ):
            raise Exception("TSL2591 device does not respond with the correct device ID")
    
    def powerOn(self):
        self.setEnable( 0x02|0x01 ) # 0x02 is ALS enable; 0x01 is power on

    def powerOff(self):
        self.setEnable( 0x00 )

    def status(self):
        return self._readRegister( 0x13 )

    def getConfig(self):
        return self._readRegister( 0x01 )

    def setConfig(self, data):
        return self._writeRegister( 0x01, data )

    def getEnable(self):
        return self._readRegister( 0x00 )

    def setEnable(self, data):
        return self._writeRegister( 0x00, data )

    def light(self):
        # Data sheet says to read these in order because it uses shadow registers to make
        # sure the low and high bytes are from the same reading.
        chan0Low  = self._readRegister(0x14)
        chan0High = self._readRegister(0x15)
        chan1Low  = self._readRegister(0x16)
        chan1High = self._readRegister(0x17)
        return (chan0High<<4 | chan0Low),(chan1High<<4 | chan1Low)
        
    def _readRegister(self, register):
        self._bus.write_byte( self._address, (0xa0 | register) )
        return self._bus.read_byte( self._address )
    
    def _writeRegister(self, register, data):
        self._bus.write_byte_data( self._address, (0xa0 | register), data )
