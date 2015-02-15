#!/usr/bin/env python
# encoding: utf-8
"""
abstract_network_device.py

These classes attempt to represent various network devices and associated
easily identifiable subsystems in an abstract way. 

Think carefully before extending these objects - not that they are perfect,
far from it, but because significantly expanding their size could be a
performance problem.

Created by Niall Richard Murphy on 2011-05-25.
Copyright (c) 2011 myself. All rights reserved.
"""

import constants
import IPy 
import os
import re
import sys
import tree

class AccessLists(object):
  """A simple (too simple) model for an access list."""
  def __init__(self):
    self.acls = {}
    self.specifications = []

  def create_and_add_acl(self, specification):
    """Extract network from specification. TODO: fixup"""
    self.specifications.append(specification) # Get rid of this TODO
    for aclid in specification:
      _tree = tree.Tree()
      for acl in specification[aclid]:
        network = acl['src']
        mask = self.de_ciscoise(acl['netm'])
        action = acl['action']
        fullnet = network + "/" + mask
        _tree.Insert(fullnet, action + " in acl " + aclid)
      self.acls[aclid] = _tree
  
  def compare_by_aclid(self, aclid, tree2):
    if (self.acls[aclid] == tree2):
      return True
    else:
      return False

  def iterate_by_aclid(self, aclid=None):
    if aclid is None:
      for aclid in self.acls:
        yield aclid
        for node in self.acls[aclid].IterateNodes():
          yield node
    else:
      for node in self.acls[aclid].IternateNodes():
        yield node

  def iterate_aclids(self):
    """TODO: uniqueify"""
    for aclid in self.acls:
      yield aclid

  def used_groups(self):
    """A specific check for usage of an ACL."""
    # TODO: implement this
    return True

  def de_ciscoise(self, wildcard_string):
    """Minging hack to make wildcard bits look like everything else.
    TODO: better place."""
    result = ""
    i = 0
    m = re.match(constants.Regex.CISCO_WILDCARD, wildcard_string)
    for octet in m.groups():
      result += str(255 - int(octet))
      if i != 3:
        result += "."
      i += 1
    return result
      

class Interface(object):
  """A simple model of a network interface.

  Currently an 'interface' potentially has addresses, a shut_state (whether it's
  down or not) and some access control lists."""
  def __init__(self):
    self.v4_addresses = []
    self.v6_addresses = []
    self.shut_state = None
    self.acls = [] # TODO: implement this/access-groups

class Route(object):
  """A simple model of a route.

  Future plans: this should be something fast and CIDRy."""
  def __init__(self):
    self.v4_networks = []
    self.v6_networks = []

class AutoInitBases(type):
  def __new__(meta, name, bases, dict):
    def new(cls):
      self = object.__new__(cls)
      for base in cls.__bases__:
        base.__init__(self)
      return self
    dict['__new__'] = new
    cls = type.__new__(meta, name, bases, dict)
    return cls

class NetworkDevice(object):
  """The base semi-abstract class for a network device.

  More concrete classes such as routers, switches, etc, inherit
  from this. Due to the potentially ginormous size of this class,
  it has been split up into separate classes that the concrete
  classes inherit from (with the help of some metaclass magic
  to call each __init__ correctly).

  Additional elements should be grouped functionally (where such
  a grouping is clear) or alphabetically (where it is not) and
  alphabetically within a function.

  I have made the slightly unusual decision to surround the device
  elements with properties (i.e., getters and setters) because I feel
  that it's better for consistency's sake to treat all elements like
  this, rather than the few I need to. I understand this is against
  strict pythonic style. Perhaps I will revisit that decision."""
  def __init__(self):
    self.parsed_config = None # Parsed configuration object.
    self._path = None # Pathname that we read the config from.
    self._interfaces = {}
    self._os_version = None

  def describe(self):
    """Return a (hopefully) unique description of the device.

    Use hostname or path to parsed file."""
    if self._hostname:
      return self._hostname
    else:
      return self._path

  def _get_os_version(self):
    return self._os_version

  def _set_os_version(self, ver):
    self._os_version = ver

  def _get_interfaces(self):
    return self._interfaces

  def _set_interfaces(self, ints):
    self._interfaces = ints

  def check_for_property_in_dict(self, property_name, supplied_dict):
    results = []
    for k, v in supplied_dict.iteritems():
      examined = v.get(property_name, None)
      if examined is not None:
        results.append(examined)
    return results

  def interface_used_access_groups(self):
    access_groups = []
    aclin = self.check_for_property_in_dict('aclin', self._interfaces)
    access_groups.extend(aclin)
    aclout = self.check_for_property_in_dict('aclout', self._interfaces)
    access_groups.extend(aclout)
    return access_groups

  def get_all_interfaces(self):
    results = []
    for k, v in self._interfaces.iteritems():
      results.append(k)
    return results

  def get_live_interfaces(self):
    live_ints = []
    for k, v in self._interfaces.iteritems():
      if v.get('shutdown', None) is None:
        live_ints.append(k)
      else:
        continue
    return live_ints

  def get_interface_properties(self, intf):
    return self._interfaces[intf]
  
  def iterate_all_interfaces(self):
    for k, v in self._interfaces:
      yield k

  def iterate_live_interfaces(self):
    live = self.get_live_interfaces()
    for elem in live:
      yield elem

  os_version = property(_get_os_version, _set_os_version)
  interfaces = property(_get_interfaces, _set_interfaces)

### Naming.

class DeviceNaming(object):
  """Things to do with name services."""
  def __init__(self):
    self._hostname = None
    self._domain_name = None
    self._resolvers = None
    
  # Hostname. We can ask for the FQDN with the 'full' parameter.
  def _get_hostname(self, full=False):
    if full:
      return constants._DNS_SEPARATOR.join([self._hostname[0], _domain_name])
    else:
      return self._hostname

  def _set_hostname(self, hn):
    self._hostname = hn

  def _get_domain_name(self):
    return self._domain_name

  def _set_domain_name(self, dn):
    self._domain_name = dn

  def _get_resolvers(self):
    return self._resolvers

  def _set_resolvers(self, res):
    self._resolvers = res

  hostname = property(_get_hostname, _set_hostname)
  domain_name = property(_get_domain_name, _set_domain_name)
  resolvers = property(_get_resolvers, _set_resolvers)


### Timing.

class DeviceTiming(object):
  """Things to do with times, NTP, etc."""
  def __init__(self):
    self._timezone = None
    self._ntp_servers = None
    self._ntp_source_int = None

  def _get_timezone(self):
    return self._timezone

  def _set_timezone(self, tz):
    self._timezone = tz

  def _get_ntp_servers(self):
    return self._ntp_servers

  def _set_ntp_servers(self, ntp):
    self._ntp_servers = ntp

  def _get_ntp_source_int(self):
    return self._ntp_source

  def _set_ntp_source_int(self, ntp):
    self._ntp_source = ntp

  ntp_servers = property(_get_ntp_servers, _set_ntp_servers)
  timezone = property(_get_timezone, _set_timezone)
  ntp_source_int = property(_get_ntp_source_int, _set_ntp_source_int)


### Network Management.

class DeviceManagement(object):
  """Things to do with network management: typically SNMP configuration."""
  def __init__(self):
    self._snmp_community = None
    self._snmp_servers = None
    self._snmp_trap_source = None
    self._snmp_version = None

  def _get_snmp_servers(self):
    return self._snmp_servers

  def _set_snmp_servers(self, snmp_list):
    self._snmp_servers = snmp_list

  def _get_trap_source(self):
    return self._snmp_trap_source

  def _set_trap_source(self, source):
    self._snmp_trap_source = source

  def _get_community(self):
    return self._snmp_community

  def _set_community(self, comm):
    self._community = comm

  def _get_version(self):
    return self._community

  def _set_version(self, ver):
    self._version = ver

  community = property(_get_community, _set_community)
  snmp_servers = property(_get_snmp_servers, _set_snmp_servers)
  snmp_trap_source = property(_get_trap_source, _set_trap_source)

### Security.

class DeviceSecurity(object):
  """A rather miscellaneous grab-bag of security related stuff."""
  def __init__(self):
    self._source_routing = None
    self._password_encryption = None
    self._ssh_server = None
    self._tacacs_servers = None
    self._tacacs_key = None
    self._acls = AccessLists()

  def _get_source_routing(self):
    return self._source_routing

  def _set_source_routing(self, sr):
    self._source_routing = sr

  def _get_password_encryption(self):
    return self._password_encryption

  def _set_password_encryption(self, pe):
    self._password_encryption = pe

  def _get_ssh_server(self):
    return self._ssh_server

  def _set_ssh_server(self, ssh):
    self._ssh_server = ssh

  def _get_acls(self):
    return self._acls.iterate_by_aclid()

  def _set_acls(self, acls):
    self._acls.create_and_add_acl(acls)

  def iterate_aclids(self):
    return self._acls.iterate_aclids()

  def _get_tacacs_servers(self):
    return self._tacacs_servers

  def _set_tacacs_servers(self, tacacs):
    self._tacacs_servers = tacacs

  def _get_tacacs_key(self):
    return self._tacacs_key

  def _set_tacacs_key(self, key):
    self._tacacs_key = key

  source_routing = property(_get_source_routing, _set_source_routing)
  password_encryption = property(_get_password_encryption, _set_password_encryption)
  ssh_server = property(_get_ssh_server, _set_ssh_server)
  acls = property(_get_acls, _set_acls)
  tacacs_servers = property(_get_tacacs_servers, _set_tacacs_servers)
  tacacs_key = property(_get_tacacs_key, _set_tacacs_key)

### Routing.

class DeviceRouting(object):
  """Things to do with device routing: static, dynamic, address families."""
  def __init__(self):
    self._static_routes = None
    self._ipv6_routing = None

  def _set_static_routes(self, sr):
    self._static_routes = sr

  def _get_static_routes(self):
    return self._static_routes

  def _set_ipv6_routing(self, sr):
    self._static_routes = sr

  def _get_ipv6_routing(self):
    return self._static_routes

  static_routes = property(_get_static_routes, _set_static_routes)
  ipv6_routing = property(_get_ipv6_routing, _set_ipv6_routing)

### Access.

class DeviceAccess(object):
  """Things to do with access to a device: consoles, vtys, etc."""
  def __init__(self):
    self._console_config = None
    self._vty_configs = None
    self._console_password = None

  def _set_console_config(self, cc):
    self._console_config = cc

  def _get_console_config(self):
    return self._console_config

  def _set_console_password(self, cp):
    self._console_password = cp

  def _get_console_password(self):
    return self._console_password
  
  def _set_vty_configs(self, vt):
    self._vty_configs = vt

  def _get_vty_configs(self, vty_selection=None):
    if vty_selection is None:
      return self._vty_configs
    else:
      return uncompress_vtys(vty_selection)

  def get_vty_config(self, vty_selection):
    return self._vty_configs[vty_selection]

  def get_vty_span(self):
    """What is the cardinal of the last vty defined?"""
    last = 0
    for k, v in self._vty_configs.iteritems():
      m = re.match(constants.Regex.VTY_COMPRESS, k)
      if m:
        first = int(m.group(1))
        second = int(m.group(2))
        if last < max(first, second):
          last = max(first, second)
    return last

  def iterate_all_vtys(self):
    """A generator for all VTYs defined for this router."""
    for k, v in self._vty_configs.iteritems():
      m = re.match(constants.Regex.VTY_COMPRESS, k)
      if m:
        bot = int(m.group(1))
        top = int(m.group(2))
        for i in xrange(bot, top + 1):
          yield {i: self._vty_configs[k]}
      else:
        yield {k: self._vty_configs[k]}
       
  def uncompress_vtys(self, selection):
    """A mostly internal method that will return the long form
    of a vty line definition for when a range has been defined.
    TODO: fix this description."""
    for k, v in self._vty_configs.iteritems():
      if k == selection:
        return self._vty_configs[k]
      m = re.match(constants.Regex.VTY_COMPRESS, k)
      if m:
        bot = int(m.group(1))
        top = int(m.group(2))
        if (selection >= bot and selection <= top):
          return self._vty_configs[k]
    return None

  def vty_used_access_groups(self):
    return self.check_for_property_in_dict('acl', self._vty_configs)
  
  console_config = property(_get_console_config, _set_console_config)
  console_password = property(_get_console_password, _set_console_password)
  vty_configs = property(_get_vty_configs, _set_vty_configs)

  
### And now the concrete objects.

class Router(NetworkDevice, DeviceNaming, DeviceTiming,
             DeviceManagement, DeviceSecurity, DeviceAccess):
  # Call the initialisers of the specified subclasses.
  __metaclass__ = AutoInitBases


class Switch(NetworkDevice):
  # Call the initialisers of the specified subclasses.
  __metaclass__ = AutoInitBases
    

class CiscoRouter(Router, NetworkDevice, DeviceNaming,
                  DeviceTiming, DeviceManagement, DeviceSecurity,
                  DeviceAccess):
  """A specific Cisco flavoured router."""
  __metaclass__ = AutoInitBases
  def __init__(self):
    super(CiscoRouter, self).__init__()
    # Things unique to Cisco go here.
    self._cdp = None


class JuniperRouter(Router, NetworkDevice, DeviceNaming,
                    DeviceTiming, DeviceManagement, DeviceSecurity,
                    DeviceAccess):
  """A specific Juniper flavoured router."""
  __metaclass__ = AutoInitBases
  def __init__(self):
    self.super().__init__()
