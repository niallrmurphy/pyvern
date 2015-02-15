#!/usr/bin/env python
# encoding: utf-8
"""
static_routing.py

Created by Niall Richard Murphy on 2011-05-30.
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
  tests = ['testStaticRoutingConsistent',]
  return unittest.TestSuite(map(TestStaticRouting, tests))


class TestStaticRouting(ti.defaultTestConfiguration):

  def testStaticRoutingConsistent(self):
    results = ti.MeetsCriteria(self.cp.routers, self.CompareRoutes)
    results = ti.IndividualAttributesDefined(self.cp.routers, 'static_routes')
    for elem in results:
      pass
    self.assertEqual(results, [])

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)

