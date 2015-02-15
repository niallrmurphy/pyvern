#!/usr/bin/env python
# encoding: utf-8
"""
test_security.py

Created by Niall Richard Murphy on 2011-06-08.
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
  tests = ['testPasswordEncryption',
           'testPasswordForConsole',
           'testSecureTransportForVTYs',
  	   #'testVtyDefined',
           'testSSHVersion2Defined',
           #'testTelnetDeprecated',
	   'testSourceRouting']
  return unittest.TestSuite(map(TestBulkSecurity, tests))

class TestBulkSecurity(ti.defaultTestConfiguration):

  def UsingSafeSSHVersion(self, router):
    if router.ssh_server is None:
      return dict(router=router.describe(), ssh_version=None)
    elif router.ssh_server is 1:
      return dict(router=router.describe(), ssh_version=1)
    else:
      return True

  def HasConsolePassword(self, router):
    if router.console_password is None:
      return None
    else:
      return True

  def HasSecureTransportForVTYs(self, router):
    for vty_entry in router.vty_configs:
      props = router.get_vty_config(vty_entry)
      inputs = props.get('inputm', "")
      if 'telnet' in inputs and 'ssh' in inputs:
        return dict(router=router.describe(), transport_includes='telnet')
      elif 'telnet' in inputs:
        return dict(router=router.describe(), transport_only='telnet')

  def HasUnreferencedACL(self, router):
    #This will only find the first un-ref'd ACL.
    for aclid in router.iterate_aclids():
      if aclid not in (router.vty_used_access_groups() or
        router.interface_used_access_groups()):
          return dict(router=router.describe(), acl=aclid)
    return True

  def HasUnACLedVTYs(self, router):
    for vt in router.iterate_all_vtys():
      v4_acl_name = vt.values()[0].get('acl', None)
      v6_acl_name = vt.values()[0].get('aclv6', None)
      if (v4_acl_name is None and v6_acl_name is None):
        return dict(router=router.describe(), vt_id=vt.keys()[0])
    return True
  
  def testPasswordEncryption(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'password_encryption')
    self.assertEqual(results, [],
      "These routers should have password encryption turned on: %s" % (results))

  def testSourceRouting(self):
    results = ti.IndividualAttributesDefined(self.cp.routers, 'source_routing')
    self.assertEqual(results, [],
      "These routers should have source routing turned off: %s" % (results))

  def testSSHVersion2Defined(self):
    results = ti.MeetsCriteriaReturnData(self.cp.routers, self.UsingSafeSSHVersion)
    self.assertEqual(results, [],
      "These routers should have ssh enabled AND ssh version 2 defined: %s" % (results))

  def testPasswordForConsole(self):
    results = ti.MeetsCriteria(self.cp.routers, self.HasConsolePassword)
    self.assertEqual(results, [],
      "These routers should have password protection on their console port: %s" % (results))

  def testSecureTransportForVTYs(self):
    results = ti.MeetsCriteriaReturnData(self.cp.routers, self.HasSecureTransportForVTYs)
    self.assertEqual(results, [],
      "These routers should have SSH transport for their VTYs: %s" % (results))

  def testUnreferencedACLs(self):
    results = ti.MeetsCriteriaReturnData(self.cp.routers, self.HasUnreferencedACL)
    self.assertEqual(results, [],
      "These routers have ACLs unreferenced by VTYs or interfaces: %s" % (results))

  def testUnappliedVTYACLs(self):
    results = ti.MeetsCriteriaReturnData(self.cp.routers, self.HasUnACLedVTYs)
    self.assertEqual(results, [],
      "These routers have some VTYs without securing ACLs applied: %s" % (results))

if __name__ == '__main__':
  suite = suite()
  unittest.main(testRunner=unittest.TextTestRunner(verbosity=2)).run(suite)
