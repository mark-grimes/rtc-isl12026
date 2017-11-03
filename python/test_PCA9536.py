#! /usr/bin/env python

"""
Tests the PCA9536 bus expander class
"""

__author__    = "Mark Grimes, Paolo Baesso"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

import unittest
import PCA9536
import smbus, datetime

class TestPCA9536(unittest.TestCase):
    def test_construction(self):
        bus = smbus.SMBus(1)
        device = PCA9536.PCA9536(bus)

    def setUp(self):
        self.device = PCA9536.PCA9536( smbus.SMBus(1) )
        
    def test_polarityReg(self):
		#device = PCA9536.PCA9536( smbus.SMBus(1) )
		testValue= 0xAA #10101010
		self.device.setInvertReg(testValue)
		res= self.device.getInvertReg()
		self.assertEqual(res, testValue)
		
		testValu= 0x55 #01010101
		self.device.setInvertReg(testValue)
		res= self.device.getInvertReg()
		self.assertEqual(res, testValue)
		
    def test_directionReg(self):
		testValue= 0xAA #10101010
		self.device.setIOReg(testValue)
		res= self.device.getIOReg()
		self.assertEqual(res, testValue)
		
		testValue= 0x55 #01010101
		self.device.setIOReg(testValue)
		res= self.device.getIOReg()
		self.assertEqual(res, testValue)
		
    def test_writeReadPin(self):
		# set pins as outputs
		self.device.setIOReg(0x00)
		# set no-inversion
		self.device.setInvertReg(0x00)
		# set outputs to a configuration (testValue)
		testValue= 0x1 
		self.device.setOutputs(testValue)
		# read the output buffer to test it
		res= self.device.getOutputs()
		self.assertEqual(res, testValue)
		# now read the input values
		# since we set the pin as outputs, this should read back equal to the testValue
		# if not, either there is a problem or something is driving the pins as mad
		res= self.device.getInputs()
		self.assertEqual((res & 0xF), (testValue & 0xF))

if __name__ == "__main__":
    unittest.main()
