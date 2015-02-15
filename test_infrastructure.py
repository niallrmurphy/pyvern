#!/usr/bin/env python
"""
test_infrastructure.py
"""

import config_parse
import constants
import os
import sys
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest

class defaultTestConfiguration(unittest.TestCase):
  """A caching class for setting up router config parsing. Should be
  inherited by every test method to avoid doing work again."""

  @classmethod
  def setUpClass(cls):
    try:
      directory = os.environ['DIR']
    except KeyError:
      directory = "example"
    try:
      pattern = os.environ['SPEC']
    except KeyError:
      pattern = '1$'
    sc = SingletonConfigCaching(directory, pattern)
    cls.cp = sc._cached['cp']

  maxDiff = None

def GroupSetCount(routers, method):
  """What is the count of routers having a particular method return True?"""
  collection = set()
  for entity in routers:
    result = getattr(entity, method, None)
    if result is not None:
      collection.add(result[0])
  return len(collection)

def IndividualAttributesDefined(routers, method):
  """Are these individual attributes defined on each router?"""
  # TODO: examples
  failures = [entity.describe()
              for entity in routers
              if getattr(entity, method, None) is None]
  return failures

def MeetsCriteria(routers, criteria_function):
  """Does each router meet this criteria function?"""
  # TODO: examples
  failures = [entity.describe()
              for entity in routers
              if not criteria_function(entity)]
  return failures

def MeetsCriteriaReturnAttribute(routers, attribute, criteria_function):
  """Does each router meet the supplied criteria function on a particular
  attribute?"""
  # TODO: examples
  failures = [MakeDict(entity.describe(), getattr(entity, attribute, None))
              for entity in routers
              if not criteria_function(entity)]
  return failures

def MeetsCriteriaReturnData(routers, criteria_function):
  """Does each router meet this criteria function; if not, return
  detailed data."""
  # TODO: examples, and yes I know type-checking is less pythonic.
  # Return a dictionary in the source test for each failing element.
  failures = [criteria_function(entity)
              for entity in routers
              if isinstance(criteria_function(entity), dict)]
  return failures

class SingletonConfigCaching(object):
  """A singleton class for caching config reading."""

  _cached = {}
  _cached['cp'] = None
  
  def __init__(self, directory, pattern):
    if self._cached['cp'] is None:
      x = config_parse.BulkConfigs(root_dir=directory)
      self._cached['cp'] = x
      self._cached['cp'].process_dir(spec=pattern,
                                     type=constants.Types.DEFAULT_CISCO)

def skipUnlessHasattr(obj, attr):
  if hasattr(obj, attr):
    return lambda func: func
  return unittest.skip("{0!r} doesn't have {1!r}".format(obj, attr))

def MakeDict(host, array):
  """An unfortunately useful function for making list comprehensions more...
  comprehensible."""
  array.sort()
  return {str(host): array}
