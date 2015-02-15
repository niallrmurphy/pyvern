#!/usr/bin/env python
# encoding: utf-8
"""
user_definitions.py

Created by Niall Richard Murphy on 2011-05-30.
"""

import re
import sys

_CORRECT_DNS_HOSTNAME_REGEXP = "^cr(.*)$|^cpe(.*)$"
_CORRECT_DNS_RESOLVERS = ['193.1.186.2', '193.1.186.3']
_CORRECT_NTP_SERVERS = ['193.1.219.116', '193.1.31.66']
_CORRECT_TACACS_SERVERS = ['193.1.219.126', '193.1.248.18']
_CORRECT_TACACS_KEY = "030E5F03001B334E1A"
_CORRECT_ACCESS_ACL = ['heanet-in-v4', 'heanet-in-v6', '99']
_CORRECT_VTY_LIMIT = 128

def isNamedCorrectly(entity):
  if re.search(_CORRECT_DNS_HOSTNAME_REGEXP, entity.hostname):
    return True
  else:
    return False

def areResolversCorrect(entity):
  for resolver in entity.resolvers:
    if resolver not in _CORRECT_DNS_RESOLVERS:
      return False
  return True

def areNTPServersCorrect(entity):
  for ntpserver in entity.ntp_servers:
    if ntpserver not in _CORRECT_NTP_SERVERS:
      return False
  return True

def hasCorrectVTYACL(entity):
  for vt in entity.iterate_all_vtys():
    v4_acl_name = vt.values()[0].get('acl', None)
    v6_acl_name = vt.values()[0].get('aclv6', None)
    if v4_acl_name not in _CORRECT_ACCESS_ACL:
      return False
  return True

# Need to verify that IPv6 is enabled on this box at all.
def hasAnyV6VTYACL(entity):
  for vt in entity.iterate_all_vtys():
    v6_acl_name = vt.values()[0].get('aclv6', None)
    if v6_acl_name is None:
      return False
  return True

def hasCorrectVTYSpan(entity):
  if entity.get_vty_span() > _CORRECT_VTY_LIMIT:
    return False
  return True

def hasCorrectTacacsServers(entity):
  for tacacs_server in entity.tacacs_servers:
    if tacacs_server not in _CORRECT_TACACS_SERVERS:
      return False
  return True
