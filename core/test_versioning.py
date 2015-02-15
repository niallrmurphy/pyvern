#!/usr/bin/env python
# encoding: utf-8
"""
test_versioning.py

All things to do with testing OS versions.

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
  tests = ['testVersionDefined',
           'testVersionMenagerie']
  return unittest.TestSuite(map(TestBulkVersioning, tests))


class TestBulkVersioning(ti.defaultTestConfiguration):

  def testVersionDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'os_version')
    self.assertEqual(results, [],
      "These routers should have OS versions available: %s" % (results))

  def testVersionMenagerie(self):
    distinct_os_versions = ti.GroupSetCount(self.cp.routers, 'os_version')
    self.assertTrue(distinct_os_versions <= 3,
      "You are probably running too many distinct OS versions on your network: %d" %
        distinct_os_versions)

if __name__ == '__main__':
  suite = suite()
  unittest.TextTestRunner(verbosity=2).run(suite)

