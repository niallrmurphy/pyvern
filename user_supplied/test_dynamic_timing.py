#!/usr/bin/env python
# encoding: utf-8
"""
test_dynamic_timing.py

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


def pytest_generate_tests(metafunc):
  for funcargs in metafunc.cls.params[metafunc.function.__name__]:
    metafunc.addcall(funcargs=funcargs)

class TestDynamicTiming(ti.defaultTestConfiguration):

  params = {
    'testNTPServersCorrect': [[x.router] for x in self.cp.routers]
  } 

  #def setUp(self):
  #  self.all_router_names = [[x.hostname] for x in self.cp.routers]
  #  self.all_router_names.sort()

  def testNTPServersCorrect(self, router):
    results = ti.MeetsCriteriaReturnAttribute(router,
                                              'ntp_servers',
                                              ud.areNTPServersCorrect)
    ud._CORRECT_NTP_SERVERS.sort()
    self.assertEqual(results, ud._CORRECT_NTP_SERVERS,
      "This router should have NTP servers matching the policy - instead it has: %s" % (
        results))

#if __name__ == '__main__':

