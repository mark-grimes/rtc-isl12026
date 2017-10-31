#! /usr/bin/env python

"""
Tests the motors on the R2D2 shield
"""

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

import unittest
import RPi.GPIO
import time

class TestMotors(unittest.TestCase):
    def test_motor1(self):
        print "Testing motor 1"
        self.performTestOnPin(24)

    def test_motor2(self):
        print "Testing motor 2"
        self.performTestOnPin(26)

    def test_motor3(self):
        print "Testing motor 3"
        self.performTestOnPin(31)

    def test_motor4(self):
        print "Testing motor 4"
        self.performTestOnPin(29)

    def test_motor5(self):
        print "Testing motor 5"
        self.performTestOnPin(7)

    def performTestOnPin(self, pinNumber):
        # This method is deliberately not called "test_..." so that unittest doesn't invoke it
        RPi.GPIO.setup( pinNumber, RPi.GPIO.OUT )
        for x in range(5):
            RPi.GPIO.output( pinNumber, not RPi.GPIO.input(pinNumber) )
            time.sleep( 0.5 )
        RPi.GPIO.output( pinNumber, 0 )

if __name__ == "__main__":
    print "Warning! This test suite makes no assertions. It requires a user to check the motors have actually fired"
    RPi.GPIO.setmode(RPi.GPIO.BOARD)
    unittest.main()
