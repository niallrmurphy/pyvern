#!/usr/bin/env python
# encoding: utf-8
"""
test_user_timing.py

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
import user_supplied.user_definitions as ud


def suite():
  tests = ['testNTPServersCorrect']
  return unittest2.TestSuite(map(TestUserTiming, tests))


class TestUserTiming(ti.defaultTestConfiguration):

  def setUp(self):
    self.all_router_names = [[x.hostname] for x in self.cp.routers]
    self.all_router_names.sort()

  def testNTPServersCorrect(self):
    results = ti.MeetsCriteriaReturnAttribute(self.cp.routers,
                                              'ntp_servers',
                                              ud.areNTPServersCorrect)
    ud._CORRECT_NTP_SERVERS.sort()
    expected = map(lambda x: ti.MakeDict(x, ud._CORRECT_NTP_SERVERS),
                   self.all_router_names)
    self.assertEqual(results, expected,
      "These routers should have NTP servers matching the policy: %s" % (
        results))

if __name__ == '__main__':
  suite = suite()
  unittest2.main(testRunner=unittest2.TextTestRunner(verbosity=2)).run(suite)

