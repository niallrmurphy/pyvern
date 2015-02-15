#!/usr/bin/env python
# encoding: utf-8
"""
config_parse.py

Created by Niall Richard Murphy on 2011-05-25.
"""

import abstract_network_device
import ciscoconfparse
import constants
import inspect
import os
import pprint
import re
import sys
import tree

class ConfigObject(object):
  """A configuration object is created to read either one config or
  tree of configs."""
  def __init__(self, root_dir):
    # Root directory is the directory where the router configs are, er, rooted.
    self.root_dir = root_dir
    self.router = None
    self.parsing_methods = {}

  # TODO(niallm): Consider name 'build_single_router'
  def process_single_file(self, path, type):
    """Process a single file given a pathname to it and a hint of its OS type.

    Future plans: autodetect config types."""
    if type == constants.Types.DEFAULT_CISCO:
      self.router = abstract_network_device.CiscoRouter()
      full_path = os.path.join(self.root_dir, path)
      self.router.parsed_config = ciscoconfparse.CiscoConfParse(full_path)
      self.router.path = full_path
    # Magically discover via introspection appropriate config parsing methods.
    self.discover_parsing_methods()
    self.call_parsing_methods(self.router)

  def discover_parsing_methods(self):
    """A slightly magic way of discovering parsing methods.

    Find via introspection subclasses of ReadConfig and their non-utility
    methods, and append them to the parsing methods dictionary, keyed
    by subclass name."""
    for subclass in ReadConfig.__subclasses__():
      for method in inspect.getmembers(subclass,
                                       predicate=inspect.ismethod):
        if method[0] not in ['__init__', 'find_lines_regexp',
                             'find_parents_child_regexp',
                             'flatten_dicts']:
          self.parsing_methods.setdefault(subclass, []).append(method[0])

  def call_parsing_methods(self, router):
    """Call each discovered parsing method on the supplied router."""
    for callables in self.parsing_methods:
      subclass_methods = self.parsing_methods[callables]
      subclass = callables(router)
      for method in subclass_methods:
        result = getattr(subclass, method)()


class BulkConfigs(ConfigObject):
  """A configuration reader intended for processing in bulk."""
  def __init__(self, root_dir):
    super(BulkConfigs, self).__init__(root_dir)
    self.routers = []

  def process_dir(self, spec, type):
    """Process a subtree of configs.

    All of them must be of the supplied type, and match the 'spec' regex."""
    self.discover_parsing_methods()
    for top, dirs, files in os.walk(self.root_dir):
      for nm in files:
        total_filename = os.path.join(top, nm)
        if not re.match(spec, total_filename):
          continue
        if type == constants.Types.DEFAULT_CISCO:
          router = abstract_network_device.CiscoRouter()
        parsed = ciscoconfparse.CiscoConfParse(total_filename)
        router.parsed_config = parsed
        router.path = total_filename
        self.call_parsing_methods(router)
        self.routers.append(router)


class ReadConfig(object):
  """Holds utility functions for reading config and being sub-classed.

  To make a new check, subclass this appropriately and extend the
  abstract router model in abstract_network_device."""
  def __init__(self, router):
    self.router = router

  def find_lines_regexp(self, regexp, named=None):
    """Find a regular expression in the config.

    Returns: either all of it, or the specific named
      variable matches."""
    total_results = []
    result = self.router.parsed_config.find_lines(regexp)
    find_obj = re.compile(regexp)
    matches = []
    for items in result:
      if named is None:
        matches = find_obj.search(items).groups()
      else:
        output = []
        for interested_result in named:
          found = find_obj.search(items).group(interested_result)
          matches.extend([found])
    total_results.extend(matches)
    return total_results

  def find_parents_child_regexp(self, parent, child, named_parent,
                                named_child, debug=None):
    """Find a regular expression in the config.

    Returns: either all of it, or a specific index."""
    if debug == None or not debug:
      debug = False
    # We can only search for one matchable thing in the parent.
    total_results = {}
    parent_matches = []
    orphan_matches = []
    # Find all parents matching parentspec.
    parents = self.router.parsed_config.find_parents_w_child(parent,
                                                             child)
    find_obj = re.compile(parent)
    find_obj2 = re.compile(child)
    for parent in parents:
      if debug:
        print "PARENT", parent
      parent_match = find_obj.search(parent).groups(named_parent)
      children = self.router.parsed_config.find_all_children(parent,
                                                             child)
      # API always returns parent, even though you care only about children,
      # so remove it from consideration.
      orphans = children[1:]
      for orphan in orphans:
        if debug:
          print "ORPHAN", orphan
        child_matches = find_obj2.search(orphan)
        prop_dict = {}
        if child_matches:
          if debug:
            print "CMATCHES", pprint.pprint(child_matches.groups())
          for name in named_child:
            if debug:
              print "NAME", name
            if child_matches.group(name) is not None:
              if debug:
                print "CONTENT", child_matches.group(name)
              prop_dict[name] = child_matches.group(name)
          if debug:
            print "PROP_DICT", prop_dict
          total_results.setdefault(parent_match[0], []).append(
            prop_dict)
    return total_results

  def flatten_dicts(self, src_dict, dest_dict):
    for k, v in src_dict.iteritems():
      pairing_dict = {}
      for pairing in src_dict[k]:
        pairing_dict.update(pairing)
      dest_dict[k] = pairing_dict
    return dest_dict

class ReadCiscoConfig(ReadConfig):
  """A specialisation of ReadConfig."""
  def __init__(self, config_handle, router):
    super(ReadCiscoConfig, self).__init__(config_handle,
                                          router)

class Versioning(ReadConfig):

  def os_version(self):
    """What is the router's OS version?"""
    find_string = ("^version (?P<ver>%s)$" % (constants.Regex.SINGLE_STRING))
    ver = self.find_lines_regexp(find_string, ['ver'])
    if len(ver) == 0:
      return None
    else:
      self.router.os_version = ver[0]
      return ver

class NetworkManagement(ReadConfig):

  def snmp_servers(self):
    """What are the router's SNMP servers?"""
    # snmp-server host 10.241.64.92 version 2c public
    find_string = ("^snmp-server host (?P<host>%s) "
                   "version (?P<ver>%s) "
                   "(.*)$" % (constants.Regex.ANY_ADDR,
                             constants.Regex.SNMP_VERSION))
    snmp_data = self.find_lines_regexp(find_string, ['host', 'ver'])
    if len(snmp_data) == 0:
      return None
    else:
      # TODO(niallm): This is pretty hacky. Find a nicer way of doing it.
      servers = snmp_data[::2]
      versions = snmp_data[1::2]
      self.router.snmp_servers = servers
      self.router.snmp_version = versions[0] # Ugh.
      return snmp_data

  def snmp_community(self):
    """What's the SNMP community string?"""
    find_string = "^snmp-server community public R[OW] (?P<comm>%s)$" % (
      constants.Regex.SINGLE_STRING)
    comm = self.find_lines_regexp(find_string, ['comm'])
    if len(comm) > 0:
      self.router.snmp_community = comm[0]
    else:
      self.router.snmp_community = None
    return comm

  def snmp_trap_source(self):
    """Where does the router send SNMP traps from?"""
    # snmp-server trap-source <int>
    find_string = "^snmp-server trap-source (?P<src>%s)" % (
      constants.Regex.INTERFACE)
    trap_source = self.find_lines_regexp(find_string, ['src'])
    self.router.trap_source = trap_source
    return trap_source


class Security(ReadConfig):

  def password_encryption(self):
    """Does the router have password encryption turned on?"""
    # service password-encryption
    find_string = "^service password-encryption"
    password_encryption = self.router.parsed_config.find_lines(find_string)
    if password_encryption:
      self.router.password_encryption = True
    else:
      self.router.password_encryption = False
    return password_encryption

  def ssh_server(self):
    """Does the router have an SSH server turned on?

    This is actually quite difficult to detect from merely static state,
    so we'll use ip ssh version as a proxy."""
    find_string = "^ip ssh version (?P<ver>%s)" % (
      constants.Regex.SSH_VERSION)
    ssh_version = self.find_lines_regexp(find_string,
                                         ['ver'])
    if ssh_version:
      self.router.ssh_server = ssh_version
    else:
      self.router.ssh_server = None
    return ssh_version

  def standard_acls(self):
    """Does the router have 'standard' ACLs? Assemble them."""
    access_list_data = self.find_lines_regexp(constants.Regex.STANDARD_ACL,
                                              ['id', 'action', 'netw', 'netm'])
    if len(access_list_data) == 0:
      return None
    results = zip(*[iter(access_list_data)] * 4) # ('1', 'permit', '204.177.154.0', '0.0.1.255')
    acldict = {}
    for access_list in results:
      aclid = access_list[0]
      action = access_list[1]
      src = access_list[2]
      netm = access_list[3]
      # CIDR conversion here
      stuffdict = {'action': action, 'src': src, 'netm': netm}
      acldict.setdefault(aclid, []).append(stuffdict)
    self.router.acls = acldict
    # {'100': [{'action': 'permit', 'src': '10.0.0.0'},
    # {'action': 'permit', 'src': '172.16.16.0'}
    return acldict

  def extended_acls(self):
    parent = "^ip access-list (standard|extended) (?P<id>%s)" % (
      constants.Regex.SINGLE_STRING)
    child = constants.Regex.EXTENDED_ACL
    access_list_data = self.find_parents_child_regexp(parent,
					              child, ['id'],
						      ['action1', 'action2',
                                                       'proto', 'netw1', 'netm1',],
                                                      False)
    # print "ACCESS_LIST_DATA", access_list_data
    return access_list_data

  def aaa_newmodel(self):
    """Does the router have AAA new-model turned on?"""
    find_string = constants.Regex.AAA_NEWMODEL
    aaa_newmodel = self.router.parsed_config.find_lines(find_string)
    if aaa_newmodel:
      self.router.aaa_newmodel = True
    else:
      self.router.aaa_newmodel = False
    return aaa_newmodel

  def tacacs_servers(self):
    """Does the router have any TACACS servers?"""
    find_string = constants.Regex.TACACS_SERVERS
    tacacs_servers = self.find_lines_regexp(find_string, ['host'])
    if len(tacacs_servers) == 0:
      # Don't have a good thing to do here yet.
      return None
    else:
      self.router.tacacs_servers = tacacs_servers
      return tacacs_servers

  def tacacs_key(self):
    """Does the router have a TACACS server key set?"""
    find_string = constants.Regex.TACACS_KEY
    tacacs_key = self.find_lines_regexp(find_string, ['key'])
    if len(tacacs_key) == 0:
      # Don't have a good thing to do here yet.
      return None
    else:
      self.router.tacacs_key = tacacs_key
  
class AntiDoS(ReadConfig):

  def source_route(self):
    """IP source routing is deprecated."""
    # no ip source-route
    find_string = "^no ip source-route"
    source_route = self.router.parsed_config.find_lines(find_string)
    if source_route:
      self.router.source_routing = False
    else:
      self.router.source_routing = True
    return source_route

class Naming(ReadConfig):

  def has_hostname(self):
    """What's the router's hostname?"""
    find_string = "^hostname (?P<host>%s)$" % (constants.Regex.SINGLE_STRING)
    hostname = self.find_lines_regexp(find_string, ['host'])
    self.router.hostname = hostname[0]
    return hostname

  def has_domain_name(self):
    """Does the router have a domain name configured?"""
    find_string = "^(ip|domain) domain[ -]name (?P<dom>%s)$" % (constants.Regex.SINGLE_STRING)
    domain_name = self.find_lines_regexp(find_string, ['dom'])
    if not domain_name:
      pass
    else:
      self.router.domain_name = domain_name[0]
    return domain_name

  def has_resolvers(self):
    """Does the router have DNS resolvers configured?"""
    find_string = "^(ip|domain) name[ -]server (?P<res>%s)$" % (constants.Regex.ANY_ADDR)
    resolver_data = self.find_lines_regexp(find_string, ['res'])
    if len(resolver_data) == 0:
      return None
    else:
      self.router.resolvers = resolver_data
      return resolver_data

class Timing(ReadConfig):

  def has_timezone(self):
    """What timezone is the router operating on?"""
    find_string = "^clock timezone (?P<tz>%s) (?P<offset>%s)$" % (
      constants.Regex.SINGLE_STRING, constants.Regex.SINGLE_STRING)
    timezone = self.find_lines_regexp(find_string, ['tz', 'offset'])
    self.router.timezone = timezone
    return timezone

  def has_ntp_servers(self):
    """Does the router have NTP servers?"""
    find_string = "^ntp server (?P<host>%s)$" % (
      constants.Regex.ANY_ADDR)
    ntp_server_data = self.find_lines_regexp(find_string, ['host'])
    if len(ntp_server_data) == 0:
      parent = "^(?P<fake>ntp)"
      child = "server (?P<host>%s)$" % (
        constants.Regex.ANY_ADDR)
      ntp_server_data = self.find_parents_child_regexp(parent, child, ['fake'],
                                                                      ['host'],
                                                       False)
      if len(ntp_server_data) == 0:
        self.router.ntp_servers = []
        return
      for server_hash in ntp_server_data['ntp']:
        host = server_hash['host']
        if self.router.ntp_servers is None:
          self.router.ntp_servers = [host]
        else:
          self.router.ntp_servers.append(host)
      return self.router.ntp_servers
    else:
      self.router.ntp_servers = ntp_server_data
      return ntp_server_data

  def has_ntp_source_int(self):
    """Does the router set a source interface for its NTP communications?"""
    find_string = "^ntp server (?P<srv>%s) source (?P<int>%s)|^ntp source (?P<int2>%s)" % (
      constants.Regex.ANY_ADDR, constants.Regex.INTERFACE,
      constants.Regex.INTERFACE)
    ntp_source_int = self.find_lines_regexp(find_string, ['int', 'int2'])
    ntp_source_int = filter(None, ntp_source_int)
    if len(ntp_source_int) == 0:
      return None
    else:
      self.router.ntp_source_int = ntp_source_int
      return ntp_source_int

class Routing(ReadConfig):

  def has_static_routes(self):
    find_string = "^ip route (?P<netw1>%s) (?P<netm1>%s) (?P<intf>%s)|" \
                  "^ip route (?P<netw2>%s) (?P<netm2>%s) (?P<destaddr>%s) (?P<metric>%s)|" \
                  "^ip route (?P<netw3>%s) (?P<netm3>%s) (?P<destnw>%s) (?P<destnm>%s)" % (
                    constants.Regex.ANY_ADDR,
                    constants.Regex.ANY_MASK,
                    constants.Regex.INTERFACE,
                    constants.Regex.ANY_ADDR,
                    constants.Regex.ANY_MASK,
                    constants.Regex.ANY_ADDR,
                    constants.Regex.ANY_METRIC,
                    constants.Regex.ANY_ADDR,
                    constants.Regex.ANY_MASK,
                    constants.Regex.ANY_ADDR,
                    constants.Regex.ANY_MASK)
    targets = ['netw1', 'netm1', 'intf',
               'netw2', 'netm2', 'destaddr', 'metric',
               'netw3', 'netm3', 'destnw', 'destnm']
    static_routes = self.find_lines_regexp(find_string, targets)
    by_interface = {}
    by_dest = {}
    for i in range(0, len(static_routes), len(targets)):
      static_route = static_routes[i:i + len(targets)]
      src_net = static_route[0] or static_route[3] or static_route[7]
      src_mask = static_route[1] or static_route[4] or static_route[8]
      src_cidr_spec = src_net + "/" + src_mask
      intf = static_route[2]
      dst_addr = static_route[5]
      metric = static_route[6]
      if dst_addr is None:
        dst_net = static_route[9]
        dst_mask = static_route[10]
      else:
        dst_net = dst_addr
        dst_mask = constants.NetworkConstants.SLASH_32
      if dst_net is not None:
        dst_cidr_spec = dst_net + "/" + dst_mask
        by_dest.setdefault(dst_cidr_spec, []).append(src_cidr_spec)
      if intf is not None:
        by_interface.setdefault(intf, []).append(src_cidr_spec)
    if len(static_routes) == 0:
      return None
    else:
      static_route_dict = by_interface.copy()
      static_route_dict.update(by_dest)
      self.router.static_routes = static_route_dict
      return static_route_dict

class Access(ReadConfig):
  """Access to the router - consoles, vtys, etc."""

  def line_console(self):
    """Does the router control console access?"""
    parent = "^line con (?P<id>.*$)"
    child = constants.Regex.CON_CONFIG
    con_transport = self.find_parents_child_regexp(parent,
                                                   child, 'id',
                                                   ['tpref', 'tout',
                                                    'timeo', 'stopb',
                                                    'encrlevel', 'passw'],
                                                   False)
    self.router.console_config = con_transport
    # Test for console password here
    # and no logging console 
    # We only care about the zeroth console for now.
    if con_transport:
      for console_spec in con_transport['0']:
        if console_spec.get('passw'):
          self.router.console_password = console_spec['passw']
        if console_spec.get('timeo'):
          self.router.console_timeouts = console_spec['timeo']
    return con_transport

  def line_vty(self):
    """Does the router control vty access?"""
    parent = "^line vty (?P<id>%s$)" % (constants.Regex.GREEDY_STRING)
    child = constants.Regex.VTY_CONFIG
    vty_transport = self.find_parents_child_regexp(parent,
                                                   child, 'id',
                                                   ['tpref', 'tout',
                                                    'timeo', 'stopb',
                                                    'encrlevel', 'passw',
                                                    'inputm', 'acl',
                                                    'acldir', 'aclv6',
                                                    'dirv6'], False)
    vty_configs = {}
    # Unsegment the partitioned dicts we get back.
    self.flatten_dicts(vty_transport, vty_configs)
    self.router.vty_configs = vty_configs
    return vty_configs


class Interfaces(ReadConfig):
  """Interfaces and addresses."""

  def interfaces(self):
    """What interfaces are on the machine, in what state, with what
    addresses?"""
    parent = "^interface (?P<int>%s)" % (constants.Regex.INTERFACE)
    child = constants.Regex.INTERFACE_PROPERTIES
    interface_properties = self.find_parents_child_regexp(parent, child, 'int',
                                                          ['addr1', 'mask1',
                                                          'addr2', 'speed',
                                                          'duplex', 'descr',
                                                          'aclin', 'aclout',
                                                          'shutdown', 'noip'],
                                                          False)
    int_config = {}
    self.flatten_dicts(interface_properties, int_config)
    self.router.interfaces = int_config

