#!/usr/bin/env python
# encoding: utf-8
"""
constants.py

Useful constants; the ones embedded in classes can be thought of as Enums.

Created by Niall Richard Murphy on 2011-05-25.
"""


_DNS_SEPARATOR = "." # What do we use to join hostname to domain name
_FIRST_ONE_ONLY = 0 # If we only want the first match back from an array


class Types(object):
  """Types of router configuration."""
  UNKNOWN=0
  DEFAULT_CISCO=1
  DEFAULT_JUNIPER=2


class Regex(object):
  """These regular expressions use named capturing groups; most of them
     are gross simplifications."""
  V4_ADDR = '((25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)\.){3}(25[0-5]|2[0-4]\d|1\d\d|[1-9]\d|\d)'
  V6_ADDR = '::'
  ANY_ADDR = '\S+'
  ANY_MASK = '\S+'
  INTERFACE = '[a-zA-Z-]+\d+(/\d+)?'
  ANY_METRIC = '\d+'
  SNMP_VERSION = '\d|\dc'
  SSH_VERSION = '1|2'
  SINGLE_STRING = '\S+'
  GREEDY_STRING = '.*'
  DIGITS = '\d+'
  STANDARD_ACL_DIGITS = '\d{1,2}'
  EXTENDED_ACL_DIGITS = '\d{3}'
  ACL_DIRECTION = 'in|out'
  ACCESS_GROUP = DIGITS
  CISCO_WILDCARD = '(\d+)\.(\d+)\.(\d+)\.(\d+)'
  ETHER_SPEED = 'nonegotiate|auto|\d+'
  ETHER_DUPLEX = 'full|half|auto'
  SHUTDOWN_STATE = 'shutdown'
  NO_IP_STATE = 'no ip address'
  VTY_COMPRESS = '(\d+)\s+(\d+)'
  ACL_PROTO = 'ip|tcp|udp'
  ACL_ACTION = 'permit|deny'
  ACL_SOURCE = '\S+'
  INTERFACE_PROPERTIES = "ip address (?P<addr1>%s) (?P<mask1>%s)|" \
                         "ipv6 address (?P<addr2>%s)|" \
                         "speed (?P<speed>%s)|" \
                         "duplex (?P<duplex>%s)|" \
                         "ip access-group (?P<aclin>%s) in|" \
                         "ip access-group (?P<aclout>%s) out|" \
                         "(?P<shutdown>%s)|" \
                         "(?P<noip>%s)|" \
                         "description (?P<descr>%s)" % (
    SINGLE_STRING, # ip address
    ANY_MASK, # mask
    SINGLE_STRING, # ip address
    ETHER_SPEED, # ethernet speed
    ETHER_DUPLEX, # ethernet duplicity
    ACCESS_GROUP, # access group
    ACCESS_GROUP, # access group
    SHUTDOWN_STATE, # shutdown state
    NO_IP_STATE, # no ip address
    GREEDY_STRING) # description
  CON_CONFIG = "transport preferred (?P<tpref>%s)|transport output (?P<tout>%s)|" \
               "exec-timeout (?P<timeo>%s\ +\d+)|stopbits (?P<stopb>%s)|" \
               "password (?P<encrlevel>%s) (?P<passw>%s)" % (
    SINGLE_STRING, # tpref
    SINGLE_STRING, # tout
    SINGLE_STRING, # timeo
    DIGITS, # stopb
    DIGITS, # encrlevel
    SINGLE_STRING) # passwd
  VTY_CONFIG = CON_CONFIG + "|transport input (?P<inputm>%s)" \
                            "|access-class (?P<acl>%s) (?P<acldir>%s)" \
                            "|ipv6 access-class (?P<aclv6>%s) (?P<dirv6>%s)" % (
    GREEDY_STRING, # inputm - could be multiple inputs supported
    SINGLE_STRING, # v4 acl
    SINGLE_STRING, # v4 direction
    SINGLE_STRING, # v6 acl
    SINGLE_STRING) # v6 direction
  STANDARD_ACL = "^access-list (?P<id>%s) (?P<action>%s) (?P<netw>%s) (?P<netm>%s)$" % (
        STANDARD_ACL_DIGITS, # id
	ACL_ACTION, # permit
	SINGLE_STRING, # 127.0.0.1
	SINGLE_STRING) # 0.0.0.255
  EXTENDED_ACL =  "(?P<action1>%s) (?P<netw1>%s) (?P<netm1>%s)|" \
            "(?P<action2>%s) (?P<proto>%s) (?P<netw2>%s) (?P<netm2>%s) (.*$)" % (
      ACL_ACTION, # permit
      ANY_ADDR, # 127.0.0.1
      SINGLE_STRING, # 0.0.0.255
      ACL_ACTION, # permit
      ACL_PROTO, # tcp
      ANY_ADDR, # 8.8.8.0
      SINGLE_STRING) # 0.0.0.255
  AAA_NEWMODEL = "^aaa new-model"
  TACACS_SERVERS = "tacacs-server host (?P<host>%s)" % (ANY_ADDR)
  TACACS_KEY = "tacacs-server key 7 (?P<key>%s)" % (SINGLE_STRING)
    
class UserClasses(object):
  CORE_ROUTER = 0
  ACCESS_ROUTER = 1
  DISTRIBUTION_ROUTER = 2

class NetworkConstants(object):
  SLASH_32 = '255.255.255.255'
