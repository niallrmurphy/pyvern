#!/usr/bin/env python
# encoding: utf-8
"""
test_user_naming.py

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
  tests = ['testHostnameCorrect',
           'testResolversCorrect']
  return unittest2.TestSuite(map(TestUserNaming, tests))


class TestUserNaming(ti.defaultTestConfiguration):

  def setUp(self):
    self.all_router_names = [[x.hostname] for x in self.cp.routers]
    self.all_router_names.sort()

  def testHostnameCorrect(self):
    results = ti.MeetsCriteria(self.cp.routers,
                               ud.isNamedCorrectly)
    results.sort()
    self.assertEqual(results, [],
      "These routers should have hostnames matching the policy: %s" % (
        results))

  def testResolversCorrect(self):
    results = ti.MeetsCriteriaReturnAttribute(self.cp.routers,
                                              'resolvers',
                                              ud.areResolversCorrect)
    results.sort()
    expected = map(lambda x: [x, ud._CORRECT_DNS_RESOLVERS],
                   self.all_router_names)
    self.assertEqual(results, expected,
      "These routers should have resolvers matching the policy: %s" % (
        results))

if __name__ == '__main__':
  suite = suite()
  unittest2.main(testRunner=unittest2.TextTestRunner(verbosity=2)).run(suite)

