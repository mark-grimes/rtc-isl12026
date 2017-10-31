#! /usr/bin/env python

"""
Tests the ISL12026 Real Time Clock class
"""

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

import unittest
import ISL12026
import smbus, datetime

class TestISL12026(unittest.TestCase):
    def test_construction(self):
        bus = smbus.SMBus(1)
        device = ISL12026.ISL12026(bus)

    def test_getStatus(self):
        device = ISL12026.ISL12026( smbus.SMBus(1) )
        status=device.getStatus()

    def test_setDate(self):
        device = ISL12026.ISL12026( smbus.SMBus(1) )
        device.setDate( datetime.datetime.now() )

if __name__ == "__main__":
    unittest.main()
