#!/usr/bin/env python
# encoding: utf-8
"""
abstract_network_device.py

Created by Niall Richard Murphy on 2011-05-25.
"""

import unittest
import abstract_network_device

class testNetworkDevice(unittest.TestCase):

  def setUp(self):
    self.router = abstract_network_device.Router()
    self.cisco = abstract_network_device.CiscoRouter()

  def testInstantiate(self):
    """Test that the metaclass stuff is working correctly."""
    self.assertEqual(self.router._hostname, None)
    self.assertEqual(self.router._timezone, None)
    self.assertEqual(self.router._snmp_community, None)

  def testInstantiateVendor(self):
    """Test that the vendor specific properties are working."""
    self.assertEqual(self.cisco._hostname, None)
    self.assertEqual(self.cisco._timezone, None)
    self.assertEqual(self.cisco._cdp, None)

if __name__ == '__main__':
  unittest.main()
