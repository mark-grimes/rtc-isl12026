#! /usr/bin/env python

"""
Tests for the TSL2591 class which talks to the TSL2591 light sensor.
"""

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

import unittest
import time
import TSL2591

class TestTSL2591(unittest.TestCase):

    def test_getRawValues(self):
        """
        Make sure we can get the raw values, and that higher gains provide higher results.
        """
        device = TSL2591.TSL2591()
        device.powerOn()

        results = {}
        for gain in [TSL2591.GAIN_LOW, TSL2591.GAIN_MED, TSL2591.GAIN_HIGH, TSL2591.GAIN_MAX]:
            device.setGain( gain )
            # need to perform a sleep because it takes a little bit of time to transition
            time.sleep(0.5)
            results[gain] = device.rawValues()

        # Channel 0 (visible and IR)
        self.assertEqual( True, results[TSL2591.GAIN_LOW][0] <= results[TSL2591.GAIN_MED][0], str(results[TSL2591.GAIN_LOW][0])+" < "+str(results[TSL2591.GAIN_MED][0]) )
        self.assertEqual( True, results[TSL2591.GAIN_MED][0] <= results[TSL2591.GAIN_HIGH][0], str(results[TSL2591.GAIN_MED][0])+" < "+str(results[TSL2591.GAIN_HIGH][0]) )
        self.assertEqual( True, results[TSL2591.GAIN_HIGH][0] <= results[TSL2591.GAIN_MAX][0], str(results[TSL2591.GAIN_HIGH][0])+" < "+str(results[TSL2591.GAIN_MAX][0]) )
        self.assertNotEqual( 0, results[TSL2591.GAIN_MAX][0] )

        # Channel 1 (IR only)
        self.assertEqual( True, results[TSL2591.GAIN_LOW][1] <= results[TSL2591.GAIN_MED][1], str(results[TSL2591.GAIN_LOW][1])+" < "+str(results[TSL2591.GAIN_MED][1]) )
        self.assertEqual( True, results[TSL2591.GAIN_MED][1] <= results[TSL2591.GAIN_HIGH][1], str(results[TSL2591.GAIN_MED][1])+" < "+str(results[TSL2591.GAIN_HIGH][1]) )
        self.assertEqual( True, results[TSL2591.GAIN_HIGH][1] <= results[TSL2591.GAIN_MAX][1], str(results[TSL2591.GAIN_HIGH][1])+" < "+str(results[TSL2591.GAIN_MAX][1]) )
        self.assertNotEqual( 0, results[TSL2591.GAIN_MAX][0] )

    def test_getAndSetGain(self):
        device = TSL2591.TSL2591()
        device.setGain( TSL2591.GAIN_LOW )
        self.assertEqual( TSL2591.GAIN_LOW, device.getGain() );
        self.assertEqual( TSL2591.GAIN_LOW, 0x30 & device._readConfigRegister() );

        device.setGain( TSL2591.GAIN_MED )
        self.assertEqual( TSL2591.GAIN_MED, device.getGain() );
        self.assertEqual( TSL2591.GAIN_MED, 0x30 & device._readConfigRegister() );

        device.setGain( TSL2591.GAIN_HIGH )
        self.assertEqual( TSL2591.GAIN_HIGH, device.getGain() );
        self.assertEqual( TSL2591.GAIN_HIGH, 0x30 & device._readConfigRegister() );

        device.setGain( TSL2591.GAIN_MAX )
        self.assertEqual( TSL2591.GAIN_MAX, device.getGain() );
        self.assertEqual( TSL2591.GAIN_MAX, 0x30 & device._readConfigRegister() );

if __name__ == "__main__":
    unittest.main()
