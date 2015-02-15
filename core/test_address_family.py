#!/usr/bin/env python
# encoding: utf-8
"""
test_address_family.py

Created by Niall Richard Murphy on 2011-10-30.
"""

import config_parse
import constants
import os
import sys
import test_infrastructure as ti
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest


def suite():
  tests = ['testIPv6AddressFamily',]
  return unittest2.TestSuite(map(TestBulkAddressFamily, tests))


class TestBulkAddressFamily(ti.defaultTestConfiguration):

  def testIPv6AddressFamily(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'ipv6_routing')
    self.assertEqual(results, [],
      "These routers should have hostnames defined: %s" % (results))

if __name__ == '__main__':
  suite = suite()
  unittest2.main(testRunner=unittest2.TextTestRunner(verbosity=2)).run(suite)
