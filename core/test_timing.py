#!/usr/bin/env python
# encoding: utf-8
"""
test_naming.py

Created by Niall Richard Murphy on 2011-05-30.
"""

import config_parse
import constants
import test_infrastructure as ti
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest

def suite():
  tests = ['testTimezoneDefined',
           'testNTPServersDefined',
           'testNTPSourceInterfaceDefined']
  return unittest.TestSuite(map(TestBulkTiming, tests))

class TestBulkTiming(ti.defaultTestConfiguration):

  def testTimezoneDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'timezone')
    self.assertEqual(results, [],
      "These routers should have a timezone defined: %s" % (results))

  def testNTPServersDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'ntp_servers')
    self.assertEqual(results, [],
      "These routers should have NTP servers defined: %s" % (results))

  def testNTPSourceInterfaceDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'ntp_source_int')
    self.assertEqual(results, [],
        "These routers should have a source interface defined "
	"for communication with the NTP servers: %s" % (results))

if __name__ == '__main__':
  suite = suite()
  unittest.TextTestRunner(verbosity=2).run(suite)
