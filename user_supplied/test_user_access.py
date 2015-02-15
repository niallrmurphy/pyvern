#!/usr/bin/env python
# encoding: utf-8
"""
test_user_access.py

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
import user_supplied.user_definitions as ud


def suite():
  tests = ['testVtySpan']
  return unittest.TestSuite(map(TestUserAccess, tests))


class TestUserAccess(ti.defaultTestConfiguration):

  def setUp(self):
    self.all_router_names = [[x.hostname] for x in self.cp.routers]
    self.all_router_names.sort()

  def testVtySpan(self):
    results = ti.MeetsCriteria(self.cp.routers, ud.hasCorrectVTYSpan)
    expected = self.all_router_names
    self.assertEqual(results, expected,
      "These routers have more VTYs defined than the policy expects: %s" % (
        results))

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)

