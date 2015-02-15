#!/usr/bin/env python
# encoding: utf-8
"""
test_user_security.py

Created by Niall Richard Murphy on 2011-10-27.
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
  tests = ['testAccessACLRestrictions']
  return unittest.TestSuite(map(TestUserTiming, tests))


class TestUserSecurity(ti.defaultTestConfiguration):

  def setUp(self):
    self.all_router_names = [[x.hostname] for x in self.cp.routers]
    self.all_router_names.sort()

  def testAccessACLRestrictions(self):
    results = ti.MeetsCriteria(self.cp.routers, ud.hasCorrectVTYACL)
    expected = self.all_router_names
    self.assertEqual(results, expected,
      "These routers should have VTY ACLs matching the policy: %s" % (
        results))

  def testIPv6ACLRestrictions(self):
    results = ti.MeetsCriteria(self.cp.routers, ud.hasAnyV6VTYACL)
    expected = self.all_router_names
    self.assertEqual(results, expected,
      "These routers should have some IPv6 VTY ACLs (if they have IPv6): %s" %
      (results))

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)

