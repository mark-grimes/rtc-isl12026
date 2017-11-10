"""
Class to talk to the TSL2591 light sensor.
"""
import smbus

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

GAIN_LOW  = 0x00  # 1x
GAIN_MED  = 0x10  # (min=22x, typical=24.5x, max=27x) for both channels
GAIN_HIGH = 0x20  # (min=360x, typical=400x, max=440x) for both channels
GAIN_MAX  = 0x30  # (min=8500x, typical=9200x, max=9900x) for channel 0; (min=9100x, typical=9900x, max=10700x) for channel 1

class TSL2591(object):

    def __init__(self, bus=None):
        if bus==None: self._bus=smbus.SMBus(1)
        else: self._bus=bus
        self._address=0x29

        # Make sure that I can correctly read the device ID (should always be 0x50)
        if( self._readRegister(0x12)!=0x50 ):
            raise Exception("TSL2591 device does not respond with the correct device ID")

        config = self._readConfigRegister()
        self._integrationTime = config & 0x07
        self._gain = config & 0x30

    def powerOn(self):
        self._writeEnableRegister( 0x02|0x01 ) # 0x02 is ALS enable; 0x01 is power on

    def powerOff(self):
        self._writeEnableRegister( 0x00 )

    def getGain(self):
        return self._gain

    def setGain(self, gain):
        if gain not in [GAIN_LOW, GAIN_MED, GAIN_HIGH, GAIN_MAX]:
            raise Exception("Invalid gain value "+str(gain))
        self._gain = gain
        self._writeConfigRegister( self._gain | self._integrationTime )

    def rawValues(self):
        return self._readChannelRegisters()

    def _readRegister(self, register):
        self._bus.write_byte( self._address, (0xa0 | register) )
        return self._bus.read_byte( self._address )

    def _writeRegister(self, register, data):
        self._bus.write_byte_data( self._address, (0xa0 | register), data )

    def _readControlRegister(self):
        return self._readRegister(0x01)

    def _writeControlRegister(self, data):
        self._writeRegister(0x01, data)

    def _readEnableRegister(self):
        return self._readRegister(0x00)

    def _writeEnableRegister(self, data):
        self._writeRegister(0x00, data)

    def _readConfigRegister(self):
        return self._readRegister(0x01)

    def _writeConfigRegister(self, data):
        self._writeRegister(0x01, data)

    def _readStatusRegister(self):
        return self._readRegister(0x13)

    def _readChannelRegisters(self):
        # Data sheet says to read these in order because it uses shadow registers to make
        # sure the low and high bytes are from the same reading.
        chan0Low  = self._readRegister(0x14)
        chan0High = self._readRegister(0x15)
        chan1Low  = self._readRegister(0x16)
        chan1High = self._readRegister(0x17)
        return (chan0High<<8 | chan0Low),(chan1High<<8 | chan1Low)
