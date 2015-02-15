#!/usr/bin/env python
# encoding: utf-8
"""
test_config_parse.py

Created by Niall Richard Murphy on 2011-05-25.
"""

import abstract_network_device
import ciscoconfparse
import config_parse
import constants
import pprint
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest


class mockParser(object):
  def __init__(self, r):
    self.r = r

  def mockParsingMethod(self):
    self.r.hostname = '42'


class TestConfigurationParsingInfrastructure(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")

  def setUpConfig(self):
    self.cp.process_single_file(path="sr05.syd01",
                                type=constants.Types.DEFAULT_CISCO)

  def testParsed(self):
    self.assertEqual(self.cp.router, None)
    self.setUpConfig()
    self.assertNotEqual(self.cp.router.parsed_config, None)

  def testParsingDiscovery(self):
    self.assertEqual(self.cp.parsing_methods, {})
    self.cp.discover_parsing_methods()
    self.assertNotEqual(self.cp.parsing_methods, None)

  def testCallParsingMethods(self):
    local_router = abstract_network_device.Router()
    fake_parsing_instance = mockParser
    self.cp.parsing_methods = {fake_parsing_instance: ['mockParsingMethod']}
    self.cp.call_parsing_methods(local_router)
    self.assertEqual(local_router.hostname, '42')

  def _setUpRouter(self):
    self.local_router = abstract_network_device.CiscoRouter()
    full_path = "example/sr05.syd01"
    self.local_router.parsed_config = ciscoconfparse.CiscoConfParse(full_path)
    self.local_router.path = full_path

  def testFindLines(self):
    self._setUpRouter()
    rc = config_parse.ReadConfig(self.local_router)
    result = rc.find_lines_regexp("^clock timezone (%s) (%s)$" % (
      constants.Regex.SINGLE_STRING, constants.Regex.SINGLE_STRING))
    self.assertEqual(result, ['PST', '-8'])
    result = rc.find_lines_regexp("^hostname (?P<hostn>%s)$" % constants.Regex.SINGLE_STRING,
      ['hostn'])
    self.assertEqual(result, ['sr05.syd01'])
    result = rc.find_lines_regexp("^ip name[ -]server (?P<dns>%s)$" % constants.Regex.SINGLE_STRING,
      ['dns'])
    self.assertEqual(result, ['172.20.0.153', '172.20.0.155'])
    result = rc.find_lines_regexp("^snmp-server community public R[OW] (?P<comm>%s)$" % (
      constants.Regex.SINGLE_STRING), ['comm'])
    self.assertEqual(result, ['1300'])
    result = rc.find_lines_regexp("^snmp-server community public R[OW] (?P<comm>%s)$" % (
      constants.Regex.SINGLE_STRING), ['comm'])
    self.assertEqual(result, ['1300'])
    result = rc.find_lines_regexp("^clock timezone (?P<tz>%s) (?P<offset>%s)$" % (
                                  constants.Regex.SINGLE_STRING, constants.Regex.SINGLE_STRING),
                                  ['tz', 'offset'])
    self.assertEqual(result, ['PST', '-8'])

  def testParentsChildrenSimple(self):
    self._setUpRouter()
    rc = config_parse.ReadConfig(self.local_router)
    parent = "ip access-list extended (?P<aclid>\S+)"
    child = "permit tcp (?P<src>\S+) (?P<mask>\S+) (?P<dst>\S+) (?P<spec>.*)$"
    result = rc.find_parents_child_regexp(parent, child,
                                          'aclid', ['src', 'mask', 'dst', 'spec'])
    self.assertIn("MANAGEMENT-ACL", result.keys())

  def testParentsChildrenComplex(self):
    self._setUpRouter()
    rc = config_parse.ReadConfig(self.local_router)
    parent = "ip access-list extended (?P<aclid>\S+)"
    child = ("permit tcp (?P<src1>\S+) (?P<mask1>\S+) (?P<dst2>\S+) (?P<mask2>\S+) (?P<spec>.*)$|" +
             "permit tcp (?P<src3>\S+) (?P<mask3>\S+) (?P<dst3>\S+) (?P<spec2>.*)$|" +
             "deny ip (?P<src4>\S+) (?P<dst4>\S+)$|" +
             "remark (?P<rem>.*)$")
    # Must have alternation here! x|y with slots, and how that works.
    result = rc.find_parents_child_regexp(parent, child,
                                          'aclid', ['src1', 'mask1', 'dst2', 'mask2', 'spec',
                                                    'src3', 'mask3', 'dst3', 'spec2',
                                                    'src4', 'dst4',
                                                    'rem'], False)
    self.assertIn("bgp-15169-neighbors-filter", result.keys())
    self.assertEqual(result['bgp-15169-neighbors-filter'][0],
                     {'rem': 'PERMITS normal bgp neighbors in 15169 addressing blocks'})

    
class TestIsolatedConfigurationParsing(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="sr05.syd01",
                                type=constants.Types.DEFAULT_CISCO)

  def testVersion(self):
    self.assertEqual(self.cp.router._os_version, "12.2")
    self.assertEqual(self.cp.router.os_version, "12.2")

  def testHostname(self):
    self.assertEqual(self.cp.router._hostname, "sr05.syd01")
    self.assertEqual(self.cp.router.hostname, "sr05.syd01")

  def testDomainName(self):
    self.assertEqual(self.cp.router._domain_name, "net.google.com")
    self.assertEqual(self.cp.router.domain_name, "net.google.com")

  def testResolvers(self):
    self.assertEqual(self.cp.router._resolvers, ['172.20.0.153', '172.20.0.155'])
    self.assertEqual(self.cp.router.resolvers, ['172.20.0.153', '172.20.0.155'])

  def testSNMP(self):
    self.assertEqual(self.cp.router.snmp_servers, ['10.241.64.92', '10.243.16.92'])
    self.assertEqual(self.cp.router.snmp_community, '1300')
    self.assertEqual(self.cp.router.snmp_version, '2c')

class TestRouting(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="sr05.syd01",
                                type=constants.Types.DEFAULT_CISCO)

  def testStaticRoutes(self):
    by_int_null0 = self.cp.router.static_routes['Null0']
    self.assertIn('192.0.2.1/255.255.255.255', by_int_null0)

class TestACLs(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="br-tra-1",
                                type=constants.Types.DEFAULT_CISCO)

  def testDeCiscoise(self):
    """It's an outrage this has to be here."""
    acl = abstract_network_device.AccessLists()
    self.assertEqual(acl.de_ciscoise("0.0.0.63"), "255.255.255.192")
    
  def testInstantiateACLs(self):
    # TODO: fix this
    acl = None
    for acl in self.cp.router.acls:
      pass
     # print acl
     #self.assertEqual(acl, {})

  def testIterateACLids(self):
    for aclid in self.cp.router.iterate_aclids():
      yield aclid
      self.assertTrue(aclid in ['1','2','3','4'])

class TestAccess(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="sr05.syd01",
                                type=constants.Types.DEFAULT_CISCO)

  def testConRead(self):
    self.assertEqual(self.cp.router.console_config,
                     {'0': [{'timeo': '30 0'}, {'stopb': '1'}]})

  def testVtyRead(self):
    self.assertEqual(self.cp.router.vty_configs,
                     {'5 15':
                          {'acldir': 'in',
                           'acl': 'MANAGEMENT-ACL',
                           'timeo': '30 15',
                           'tpref': 'none',
                           'inputm': 'ssh'},
                      '0 4': 
                          {'acldir': 'in',
                           'acl': 'MANAGEMENT-ACL',
                           'timeo': '30 0',
                           'tpref': 'none',
                           'inputm': 'ssh'}})

  def testGetVtyConfig(self):
    self.assertEqual(self.cp.router.get_vty_config('0 4'),
                     {'acldir': 'in',
                      'acl': 'MANAGEMENT-ACL',
                      'timeo': '30 0',
                      'tpref': 'none',
                      'inputm': 'ssh'})

  def testVtyCompression(self):
    self.assertEqual(self.cp.router.uncompress_vtys(4),
                     {'acldir': 'in',
                      'acl': 'MANAGEMENT-ACL',
                      'timeo': '30 0',
                      'tpref': 'none',
                      'inputm': 'ssh'})
    self.assertEqual(self.cp.router.uncompress_vtys(13),
                     {'acl': 'MANAGEMENT-ACL',
                      'acldir': 'in',
                      'inputm': 'ssh',
                      'timeo': '30 15',
                      'tpref': 'none'})

  def testVtyIteration(self):
    for x in self.cp.router.iterate_all_vtys():
      index = x.keys()[0]
      if (index >= 0 and index <= 4):
        self.assertEqual(x, {index:
                     {'acldir': 'in',
                      'acl': 'MANAGEMENT-ACL',
                      'timeo': '30 0',
                      'tpref': 'none',
                      'inputm': 'ssh'}})
      elif (index > 4 and index <= 15):
        self.assertEqual(x, {index:
                     {'acldir': 'in',
                      'acl': 'MANAGEMENT-ACL',
                      'timeo': '30 15',
                      'inputm': 'ssh',
                      'tpref': 'none'}})
      else:
        self.assertEqual(1,0)

  def testVtySpan(self):
    self.assertEqual(self.cp.router.get_vty_span(), 15)

  def testVtyAccessGroups(self):
    self.assertEqual(self.cp.router.vty_used_access_groups(),
                     ['MANAGEMENT-ACL', 'MANAGEMENT-ACL']) # TODO: fix dupes

class TestRoutes(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.BulkConfigs(root_dir="example")
    self.cp.process_dir(type=constants.Types.DEFAULT_CISCO, spec=".*1$")

  def testRoutesRead(self):
    #self.assertEqual(self.cp.router.
    pass

class TestInterfaces(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="br-tra-1",
                                type=constants.Types.DEFAULT_CISCO)

    
  def testInterfaces(self):
    self.assertDictContainsSubset(
      {'GigabitEthernet2/19': {'noip': 'no ip address',
                               'descr': 'Po11 --> dub3-br-cor-r2 Gi2/1'}},
      self.cp.router.interfaces)
    self.assertDictContainsSubset(
      {'Loopback0': {'mask1': '255.255.255.255', 'addr1': '83.238.81.1'}},
                                  self.cp.router.interfaces)

  def generateInterfaceList(self):
    intlist = []
    for z in range(1,3):
      intlist.append('GigabitEthernet1/%s' % z)
    for x in range(1,49):
      intlist.append('GigabitEthernet2/%s' % x)
    for y in range(1,9):
      intlist.append('GigabitEthernet3/%s' % y)
    for q in range(1,3):
      intlist.append('Port-channel%s' % q)
    intlist.append('Port-channel11')
    intlist.append('Loopback0')
    intlist.append('Vlan1')
    return intlist

  def generateLiveInterfaceList(self):
    intlist = []
    for x in range(1,3):
      intlist.append('GigabitEthernet2/%s' % x)
    for y in range(19,21):
      intlist.append('GigabitEthernet2/%s' % y)
    for z in range(25,27):
      intlist.append('GigabitEthernet2/%s' % z)
    for q in range(7,9):
      intlist.append('GigabitEthernet2/%s' % q)
    intlist.append('GigabitEthernet2/31')
    intlist.append('GigabitEthernet2/13')
    intlist.append('GigabitEthernet3/1')
    intlist.append('Port-channel11')
    intlist.append('Port-channel1')
    intlist.append('Port-channel2')
    intlist.append('Loopback0')
    return intlist

  def testInterfaceAccessGroups(self):
    self.assertEqual(self.cp.router.interface_used_access_groups(), ['100','101'])

  def testGetAllInterfaces(self):
    intlist = self.generateInterfaceList()
    foundlist = self.cp.router.get_all_interfaces()
    self.assertItemsEqual(intlist,
                          foundlist)

  def testGetLiveInterfaces(self):
    gintlist = self.generateLiveInterfaceList()
    lintlist = self.cp.router.get_live_interfaces()
    gintlist.sort()
    lintlist.sort()
    self.assertItemsEqual(gintlist, lintlist)
  
class TestBulkConfigurationParsing(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.BulkConfigs(root_dir="example")
    self.cp.process_dir(type=constants.Types.DEFAULT_CISCO, spec=".*1$")

  def testParsed(self):
    for entity in self.cp.routers:
      self.assertNotEqual(entity, None)
    for entity in self.cp.routers:
      rc = entity.parsed_config
      self.assertNotEqual(rc, None)

  def testNaming(self):
    for entity in self.cp.routers:
      self.assertTrue(entity.hostname in ['acc-sw-10-43-22', 'dub3-br-tra-r1', 'sr05.syd01'])
      self.assertTrue(entity.domain_name in ['amazon.com', 'net.google.com'])

class TestBulkSecurity(unittest.TestCase):

  def setUp(self):
    self.cp = config_parse.ConfigObject(root_dir="example")
    self.cp.process_single_file(path="br-tra-1",
                                type=constants.Types.DEFAULT_CISCO)

  def testSSHVersions(self):
    self.assertIn(self.cp.router.ssh_server, [None, 1, 2])

  def testTACACSServers(self):
    self.assertIn(self.cp.router.tacacs_servers, ['127.0.0.1'])
      
if __name__ == '__main__':
  unittest.main()

#     parent = "router bgp (?P<asnumber>\S+)"
#    child = ("neighbor (?P<neigh>\S+) peer-group (?P<groupname>\S+)|" +
#             "neighbor (?P<neigh2>\S+) remote-as (?P<asname>\S+)|" +
#             "neighbor (?P<neigh3>\S+) description (?P<descr>.*)|" +
#             "maximum-paths (?P<maxp>.*)$")
    # Must have alternation here! x|y with slots, and how that works.
#    result = rc.find_parents_child_regexp(parent, child,
#                                          'asnumber', ['neigh', 'groupname',
#                                                       'neigh2', 'asname',
#                                                       'neigh3', 'descr',
#                                                       'maxp'], True)
