#!/usr/bin/env python
# encoding: utf-8
"""
test_naming.py

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
  tests = ['testHostnameDefined',
           'testDomainNameDefined',
           'testResolversConfigured']
  return unittest.TestSuite(map(TestBulkNaming, tests))


class TestBulkNaming(ti.defaultTestConfiguration):

  def testHostnameDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'hostname')
    self.assertEqual(results, [],
      "These routers should have hostnames defined: %s" % (results))

  def testDomainNameDefined(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'domain_name')
    self.assertEqual(results, [],
      "These routers should have domain names defined: %s" % (results))

  def testResolversConfigured(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'resolvers')
    self.assertEqual(results, [],
      "These routers should have resolvers defined: %s" % (results))

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)
