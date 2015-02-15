#!/usr/bin/env python
# encoding: utf-8
"""
test_interfaces.py

Created by Niall Richard Murphy on 2011-10-30.
"""

import config_parse
import constants
import os
import test_infrastructure as ti
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest


def suite():
  tests = ['testLoopbackConfigured',]
  return unittest.TestSuite(map(TestBulkInterfaces, tests))


class TestBulkInterfaces(ti.defaultTestConfiguration):

  def HasDefinedLoopbackWithAddresses(self, router):
    l0 = router.interfaces.get('Loopback0', None)
    addr1 = l0.get('addr1', None)
    addr2 = l0.get('addr2', None)
    if l0 is None:
      return False
    elif l0 is not None and (addr1 is None and addr2 is None):
      return False
    else:
      return True
    
  def testLoopbackConfigured(self):
    results = ti.MeetsCriteria(self.cp.routers, self.HasDefinedLoopbackWithAddresses)
    self.assertEqual(results, [],
      "These routers should have a loopback interface with a defined address: %s" %
      (results))

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)
