#! /usr/bin/env python

"""
Tests for the TSL2591 class which talks to the TSL2591 light sensor.
"""

__author__    = "Mark Grimes"
__copyright__ = "Copyright 2017, Rymapt Ltd"
__license__   = "To be decided"

import unittest
import TSL2591

class TestTSL2591(unittest.TestCase):
    def test_construct(self):
        device=TSL2591.TSL2591()


if __name__ == "__main__":
    unittest.main()
