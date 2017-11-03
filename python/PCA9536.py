# -*- coding: utf-8 -*-

"""
Class to talk to the PCA9536 bus expander.
"""
import smbus

__author__    = "Paolo Baesso"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

class PCA9536(object):
    def __init__(self, bus=None):
        if bus==None: self._bus=smbus.SMBus(1)
        else: self._bus=bus
        self._address=0x41

    #Class to configure the expander modules

    def _readRegister(self, register):
        if( register < 0) | ( register > 3 ):
            raise Exception("PCA9536 readRegister: register must be in range [0,3]")
        self._bus.write_byte( self._address, register )
        return self._bus.read_byte( self._address )

    def _writeRegister(self, register, data):
        if( register < 0) | ( register > 3 ):
            raise Exception("PCA9536 writeRegister: register must be in range [0,3]")
        self._bus.write_byte_data( self._address, register, data )

    def setInvertReg(self, polarity= 0x00):
        #Set the content of register 4 or 5 which determine the polarity of the
        #ports (0= normal, 1= inverted).
        polarity = polarity & 0xFF
        self._writeRegister(2, polarity)

    def getInvertReg(self):
        #Read the content of register 4 or 5 which determine the polarity of the
        #ports (0= normal, 1= inverted).
        return self._readRegister(2)

    def setIOReg(self, direction= 0xFF):
        #Set the content of register 6 or 7 which determine the direction of the
        #ports (0= output, 1= input).
        direction = direction & 0xFF
        self._writeRegister(3, direction)

    def getIOReg(self):
        #Read the content of register 6 or 7 which determine the direction of the
        #ports (0= normal, 1= input).
        return self._readRegister(3)

    def getInputs(self):
        #Read the incoming values of the pins for one of the two 8-bit banks.
        return self._readRegister(0)

    def getOutputs(self):
        #Read the incoming values of the pins for one of the two 8-bit banks.
        return self._readRegister(1)

    def setOutputs(self, values= 0x00):
        #Set the content of the output flip-flops.
        values = values & 0xFF
        self._writeRegister(1, values)
