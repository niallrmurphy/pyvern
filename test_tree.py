#!/usr/bin/env python
# encoding: utf-8
# Niall Richard Murphy <niallm@gmail.com>

"""Test the tree (gap-production) object."""

import sys
import constants
import random
import tree
# Perhaps unittest2 is available. Try to import it, for
# those cases where we are running python 2.7.
try:
    import unittest2 as unittest
except ImportError:
    import unittest

class NodeTest(unittest.TestCase):

  def setUp(self):
    self.n = tree.Node(supplied_data = "Test")
    self.n2 = tree.Node(supplied_data = "Test2")
    self.n3 = tree.Node(supplied_data = "Test3")
    self.n4 = tree.Node(supplied_data = "Test4")
    self.n5 = tree.Node(supplied_data = "Test5")

  def test_node_get_used(self):
    self.failUnless(self.n.used == False)

  def test_node_set_used(self):
    self.n.used = True
    self.failUnless(self.n.used == True)

  def test_node_get_data(self):
    self.failUnless(self.n.GetData() == "Test")

  def test_node_set_data(self):
    self.n.SetData("Wobble")
    self.failUnless(self.n.GetData() == "Wobble")

  def test_node_getset_left(self):
    self.n.SetLeft(self.n2)
    self.failUnless(self.n.GetLeft() == self.n2)

  def test_node_getset_right(self):
    self.n.SetRight(self.n2)
    self.failUnless(self.n.GetRight() == self.n2)

  def test_node_getset_parent(self):
    self.n.SetLeft(self.n2)
    self.n2.SetParent(self.n)
    self.n.SetRight(self.n3)
    self.n3.SetParent(self.n)
    self.failUnless(self.n2.GetParent() == self.n)
    self.failUnless(self.n3.GetParent() == self.n)

  def test_node_getset_level(self):
    self.assertEqual(self.n.GetLevel(), 0)
    self.n2.SetParent(self.n)
    self.n.SetLeft(self.n2)
    self.assertEqual(self.n2.GetLevel(), 1)
    self.n2.SetLeft(self.n3)
    self.n3.SetParent(self.n2)
    self.assertEqual(self.n3.GetLevel(), 2)

  def test_node_getset_leftright(self):
    self.n.SetLeft(self.n2)
    self.n2.SetParent(self.n)
    self.n.SetRight(self.n3)
    self.n3.SetParent(self.n)
    self.assertEqual(self.n2.AmLeft(), True)
    self.assertEqual(self.n3.AmRight(), True)

  def test_node_amroot(self):
    self.assertEqual(self.n.AmRoot(), True)

  def test_node_getbinary(self):
    self.n.SetLeft(self.n2)
    self.n2.SetParent(self.n)
    self.n.SetRight(self.n3)
    self.n3.SetParent(self.n)
    self.assertEqual(self.n2.GetBinary(), 0)
    self.assertEqual(self.n3.GetBinary(), 1)

  def test_node_get_path(self):
    self.n.SetLeft(self.n2)
    self.n2.SetParent(self.n)
    self.n.SetRight(self.n3)
    self.n3.SetParent(self.n)
    self.n4.SetParent(self.n2)
    self.n5.SetParent(self.n2)
    self.n2.SetLeft(self.n4)
    self.n2.SetRight(self.n5)
    self.assertEqual(self.n2.GetPath(), "0")
    self.assertEqual(self.n3.GetPath(), "1")
    self.assertEqual(self.n4.GetPath(), "00")
    self.assertEqual(self.n5.GetPath(), "01")

class TreeTest(unittest.TestCase):

  def setUp(self):
    self.t = tree.Tree()

  def structuralSetUp(self):
    # Setup for structual comparisons & marking-as-used
    self.n = tree.Node(supplied_data = "Root")
    self.n2 = tree.Node(supplied_data = "Test2")
    self.n3 = tree.Node(supplied_data = "Test3")
    self.n4 = tree.Node(supplied_data = "Test4")
    self.n5 = tree.Node(supplied_data = "Test5")
    self.n6 = tree.Node(supplied_data = "Test6")
    self.n7 = tree.Node(supplied_data = "Test7")
    self.t.SetRoot(self.n)
    self.t.GetRoot().SetLeft(self.n2)
    self.n2.SetParent(self.n)
    self.t.GetRoot().GetLeft().SetLeft(self.n3)
    self.n3.SetParent(self.n2)
    self.t.GetRoot().GetLeft().SetRight(self.n4)
    self.n4.SetParent(self.n2)
    self.t.GetRoot().SetRight(self.n5)
    self.n5.SetParent(self.n)
    self.t.GetRoot().GetRight().SetLeft(self.n6)
    self.n6.SetParent(self.n5)
    self.t.GetRoot().GetRight().SetRight(self.n7)
    self.n7.SetParent(self.n5)
    self.n3.used = True
    self.n4.used = True
    self.n6.used = True
    self.n7.used = True
  
  def test_tree_new(self):
    self.failUnless('Insert' in dir(self.t))

  def test_tree_path_to_dot_quad(self):
    binstr = "1111"
    x = self.t.PathToDotQuad(binstr, 4)
    self.assertEqual(x, "240.0.0.0/4")
    binstr = "10100111111"
    y = self.t.PathToDotQuad(binstr, 16)
    self.assertEqual(y, "167.224.0.0/16")

  def test_tree_get_root_properties(self):
    self.failUnless(self.t.GetRoot().GetData() == 'Root')
    self.failUnless(self.t.GetRoot().GetLeft() == None)
    self.failUnless(self.t.GetRoot().GetRight() == None)
    self.failUnless(self.t.GetRoot().GetParent() == None)

  def test_tree_generate_for_prefix(self):
    for x in self.t.GenerateForPrefix(2):
      self.failUnless(x in ['0.0.0.0/2', '64.0.0.0/2', 
                            '128.0.0.0/2', '192.0.0.0/2'])

  def test_tree_insert_default_route(self):
    obj = self.t.Insert('0.0.0.0/0', "test03point5", test_dup = False)
    self.assertEqual(obj, self.t.GetRoot())

  def test_tree_structural_comparison(self):
    #      N
    #   N2   N5
    # N3 N4 N6 N7
    self.structuralSetUp()
    for x in self.t.IterateNodes():
      self.failUnless(x in ['0.0.0.0/2', '64.0.0.0/2', 
                            '128.0.0.0/2', '192.0.0.0/2'])
    self.t2 = tree.Tree()
    self.t2.Insert('0.0.0.0/2', 'structural')
    self.t2.Insert('64.0.0.0/2', 'structural')
    self.t2.Insert('128.0.0.0/2', 'structural')
    self.t2.Insert('192.0.0.0/2', 'structural')
    for x in self.t2.IterateNodes():
      self.failUnless(x in ['0.0.0.0/2', '64.0.0.0/2', 
                            '128.0.0.0/2', '192.0.0.0/2'])

  def test_tree_follow_chain(self):
    self.t.Insert('192.168.0.0/16', 'test_tree_follow_chain')
    obj = self.t.Lookup('192.168.0.0/16')
    current = obj
    self.assertEqual(current.GetLevel(), 16)
    while current != self.t.root:
      old_level = current.GetLevel()
      current = current.GetParent()
      new_level = current.GetLevel()
      self.assertEqual(old_level, new_level + 1)
    # TODO(niallm): check for membership of array [n - level] -> 192.168.0.0 here
    self.t.Insert('192.169.0.0/16', 'test_tree_follow_chain_2')
    new_obj = self.t.Lookup('192.169.0.0/16', 'test_tree_follow_chain_3')
    self.assertEqual(obj.GetParent(), new_obj.GetParent())

  def test_tree_recursive_marking(self):
    self.structuralSetUp()
    self.assertEqual(self.n2.used, False)
    self.t.CheckRecursivelyUsed(self.n3)
    self.assertEqual(self.n2.used, True)
    self.assertEqual(self.n.used, False)
    self.n5.used = True
    self.t.CheckRecursivelyUsed(self.n3)
    self.assertEqual(self.n.used, True)

  def test_tree_insert_one_prefix_left(self):
    obj = self.t.Insert('0.0.0.0/1', "testInsertSmall")
    data = obj.GetData()
    used = obj.used
    left = obj.GetLeft()
    right = obj.GetRight()
    parent = obj.GetParent()
    level = obj.GetLevel()
    root = self.t.GetRoot()
    self.assertEqual(data, "testInsertSmall")
    self.assertEqual(used, True)
    self.assertEqual(parent, root)
    self.assertEqual(left, None)
    self.assertEqual(right, None)
    self.failUnless(obj.GetParent().GetLeft() == obj)
    self.assertEqual(level, 1)

  def test_tree_insert_flags(self):
    result = self.t.Insert('0.0.0.0/8', '4.5treeobj', mark_used = False, 
                         test_used = True, test_none = False)
    self.assertEqual(result.used, False)

  def test_tree_insert_two_prefixes_getbinary(self):
    obj = self.t.Insert('0.0.0.0/1', "testInsertSmall")
    bin = obj.GetBinary()
    self.failUnless(str(bin) == "0")
    obj = self.t.Insert('128.0.0.0/1', "testInsertSmall")
    bin = obj.GetBinary()
    self.failUnless(str(bin) == "1")

  def test_tree_insert_one_prefix_right(self):
    obj = self.t.Insert('128.0.0.0/1', "testInsertSmall")
    data = obj.GetData()
    used = obj.used
    left = obj.GetLeft()
    right = obj.GetRight()
    parent = obj.GetParent()
    level = obj.GetLevel()
    path = obj.GetPath()
    self.assertEqual(data, "testInsertSmall")
    self.assertEqual(used, True)
    self.assertEqual(parent, self.t.GetRoot())
    self.assertEqual(left, None)
    self.assertEqual(right, None)
    self.assertEqual(obj.GetParent().GetRight(), obj)
    self.assertEqual(level, 1)
    self.assertEqual(path, "1")

  def test_tree_insert_one_longer_prefix(self):
    obj = self.t.Insert('10.0.0.0/8', "testInsertLarge")
    data = obj.GetData()
    used = obj.used
    left = obj.GetLeft()
    right = obj.GetRight()
    parent = obj.GetParent()
    level = obj.GetLevel()
    path = obj.GetPath()
    self.failUnless(obj.GetData() == 'testInsertLarge')
    self.assertEqual(right, None)
    self.assertEqual(left, None)
    self.assertEqual(level, 8)
    self.assertEqual(path, "00001010")

  def test_tree_get_path_to_real_prefix(self):
    obj = self.t.Insert('10.0.0.0/8', "testGetPath")
    path = obj.GetPath()
    self.failUnless(path == "00001010", "unexpected path to node: [%s] " % path)
    obj = self.t.Insert('137.43.0.0/16', "testInsertLarge")
    path = obj.GetPath()
    self.failUnless(path == "1000100100101011", "unexpected path to node: [%s] " % path)

  def test_tree_lookup_succeed(self):
    obj = self.t.Insert('10.0.0.0/8', "testLookup")
    obj2 = self.t.Lookup('10.0.0.0/8')
    self.assertEqual(obj, obj2)

  def test_tree_lookup_fail(self):
    obj = self.t.Insert('10.0.0.0/8', "testNegLookup")
    obj2 = self.t.Lookup('127.0.0.1')
    self.assertEqual(obj2, None)
    self.assertNotEqual(obj, None)

  def test_tree_lookup_funky(self):
    for count in range(4,12):
      objdict = {}
      total_route_set = []
      for route in self.t.GenerateForPrefix(count):
        total_route_set.append(route)
      picks = random.sample(total_route_set, count/2)
      for item in picks:
        objdict[item] = self.t.Insert(item, 
                                      "complex_find_gap", mark_used = False)
      for item in total_route_set:
        if item in picks:
          self.assertEqual(self.t.Lookup(item), objdict[item], 
                           "Picks lookup [%s] got [%s]" % (self.t.Lookup(item), 
                                                       objdict[item]))
        else:
          self.assertEqual(self.t.Lookup(item), None, 
                           "Non-picks lookup get [%s] not none" % 
                           self.t.Lookup(item))

  def test_insert_duplicate_fails(self):
    #self.t.debug=30
    obj1 = self.t.Insert('137.43.0.0/16', 'testInsertDup')
    self.assertEqual(False, self.t.Insert('137.43.0.0/16', 
                                          'testInsertDup'))
    #self.t.debug=0
          
  def test_tree_quick_insert_multiple_prefixes(self):
    obj1 = self.t.Insert('0.0.0.0/8', "testInsertMultiple")
    obj2 = self.t.Insert('1.0.0.0/8', "testInsertMultiple")
    data1 = obj1.GetData()
    used1 = obj1.used
    left1 = obj1.GetLeft()
    right1 = obj1.GetRight()
    parent1 = obj1.GetParent()
    level1 = obj1.GetLevel()
    left2 = obj2.GetLeft()
    right2 = obj2.GetRight()
    parent2 = obj2.GetParent()
    level2 = obj2.GetLevel()
    self.assertEqual(data1, 'testInsertMultiple')
    self.assertEqual(left1, None)
    self.assertEqual(left2, None)
    self.assertEqual(level1, 8)
    self.assertEqual(level2, 8)

class TreeTestGaps(unittest.TestCase):

  def setUp(self):
    self.t = tree.Tree()


  def test_tree_quick_find_gap_vanilla(self):
    # Simple insert
    self.t.Insert('0.0.0.0/8', "testFindGap")
    ret = self.t.FindGap(8)
    self.assertEqual(ret, "1.0.0.0/8", 
                     "Find gap returned [%s], not 1.0.0.0/8" % ret)
    # Route of same length immediately beside
    self.t.Insert('1.0.0.0/8', "testFindGap2")
    ret2 = self.t.FindGap(8)
    self.assertEqual(ret2, "2.0.0.0/8", 
                     "Find gap returned [%s], not 2.0.0.0/8" % ret2)
    # And up two levels and down again
    self.t.Insert("2.0.0.0/8", "testFindGap")
    ret3 = self.t.FindGap(8)
    self.assertEqual(ret3, "3.0.0.0/8",
                     "Find gap returned [%s], not " % ret3)
    # Insert covering route (0-3/8)
    self.t.Insert("0.0.0.0/6", "testFindGap")
    ret4 = self.t.FindGap(6)
    self.assertEqual(ret4, "4.0.0.0/6")
    # Find a large gap after some small routes inserted
    self.t.Insert("0.0.0.0/4", "testFindGap")
    ret5 = self.t.FindGap(6)
    self.assertEqual(ret5, "16.0.0.0/6")
    # Bang over to the other side of the tree altogether
    ret6 = self.t.FindGap(1)
    self.assertEqual(ret6, "128.0.0.0/1")

  def test_tree_quick_find_gap_random(self):
    for count in range(1,10):
      self.t = None
      self.t = tree.Tree()
      # Looking for route with a relevant prefix size.
      # Generate a list of all possible prefixes leaving out one at random.
      total_route_set = []
      for route in self.t.GenerateForPrefix(count):
        total_route_set.append(route)
      remove_me = random.choice(total_route_set)
      total_route_set.remove(remove_me)
      for item in total_route_set:
        obj1 = self.t.Insert(item, "testFindGap2")
      found = self.t.FindGap(count)
      self.assertEqual(found, remove_me, "Find gap gave [%s] not expected \
        [%s]" % (found, remove_me))

  def test_tree_different_size_find_gap(self):
    self.t.Insert('0.0.0.0/8', 'reason1')
    self.t.Insert('1.0.0.0/8', 'reason2')
    r1 = self.t.FindGap(8)
    self.assertEqual(r1, '2.0.0.0/8')
    self.t.Insert(r1, 'reason1')
    r2 = self.t.FindGap(8)
    self.assertEqual(r2, '3.0.0.0/8')
    self.t.Insert(r2, 'reason2')
    r3 = self.t.FindGap(20)
    self.assertEqual(r3, '4.0.0.0/20')
    self.t.Insert(r3, 'reason3')
    r4 = self.t.FindGap(8)
    self.assertEqual(r4, '5.0.0.0/8')
    r5 = self.t.FindGap(10)
    self.assertEqual(r5, '4.64.0.0/10')
    self.t.Insert(r5, 'reason5')
    r6 = self.t.FindGap(6)
    self.assertEqual(r6, '8.0.0.0/6')
    r7 = self.t.FindGap(30)
    self.assertEqual(r7, '4.0.16.0/30')

  def test_tree_different_size_find_gap_from(self):
    #self.t.debug = 10
    self.t.Insert('0.0.0.0/8', 'reason1')
    self.t.Insert('1.0.0.0/8', 'reason2')
    r1 = self.t.FindGapFrom('0.0.0.0/1', 8)
    self.assertEqual(r1, '2.0.0.0/8')
    self.t.Insert(r1, 'reason1')
    r2 = self.t.FindGapFrom('0.0.0.0/1', 8)
    self.assertEqual(r2, '3.0.0.0/8')
    self.t.Insert(r2, 'reason2')
    r3 = self.t.FindGapFrom('0.0.0.0/1', 20)
    self.assertEqual(r3, '4.0.0.0/20')
    self.t.Insert(r3, 'reason3')
    r4 = self.t.FindGapFrom('0.0.0.0/1', 8)
    self.assertEqual(r4, '5.0.0.0/8')
    r5 = self.t.FindGapFrom('0.0.0.0/1', 10)
    self.assertEqual(r5, '4.64.0.0/10')
    self.t.Insert(r5, 'reason5')
    r6 = self.t.FindGapFrom('0.0.0.0/1', 6)
    self.assertEqual(r6, '8.0.0.0/6')
    r7 = self.t.FindGapFrom('0.0.0.0/1', 30)
    self.assertEqual(r7, '4.0.16.0/30')
        
  def test_tree_find_gap(self):
    for count in range(4,12):
       total_route_set = []
       for route in self.t.GenerateForPrefix(count):
         total_route_set.append(route)
       picks = random.sample(total_route_set, count/2)
       for item in picks:
         obj1 = self.t.Insert(item, "testFindGap3")
       for item in picks:
         gap = self.t.FindGap(count)
         self.failUnless(gap in total_route_set, "Gap found [%s] not in total \
         route set!" % gap)
         if gap not in picks:
           # Add it and try again
           self.t.Insert(gap, "testFindGap3Update")
         else:
           print "??????"

  def test_tree_find_gap_from_simple(self):
    self.t.Insert("0.0.0.0/8", 'testFindGapFrom', mark_used = False, 
                  test_none = False)
    gap = self.t.FindGapFrom("0.0.0.0/8", 24)
    self.assertEqual(gap, "0.0.0.0/24", 
                     "Should find 0.0.0.0/24, instead found [%s]" % gap)
    gap = self.t.FindGapFrom("1.0.0.0/8", 24)
    self.assertEqual(gap, None, 
                     "Should find no gap, instead got [%s]" % gap)

  def test_tree_find_gap_from_simple_higher(self):
    self.t.Insert("0.0.0.0/8", 'testFindGapFrom', mark_used = False, 
                  test_none = False)
    gap = self.t.FindGapFrom("0.0.0.0/8", 7)
    self.assertEqual(gap, None,
                     "Should find no gap, instead got [%s]" % gap)

  def test_tree_find_gap_from_simple_samesize(self):
    self.t.Insert("0.0.0.0/8", 'testFindGapFrom', mark_used = False, 
                  test_none = False)
    gap = self.t.FindGapFrom("0.0.0.0/8", 8)
    self.assertEqual(gap, "0.0.0.0/8")

  def test_tree_find_gap_from_middling(self):
    self.t.Insert("172.16.0.0/12", "findgapmiddling", mark_used = False,
                  test_none = False)
    gap = self.t.FindGapFrom("172.16.0.0/12", 16)
    self.assertEqual(gap, "172.16.0.0/16")
    self.t.Insert("172.16.0.0/16", "findgapmiddling")
    gap = self.t.FindGapFrom("172.16.0.0/12", 16)
    self.assertEqual(gap, "172.17.0.0/16")
    self.t.Insert("172.17.0.0/16", "findgapmiddling")
    gap = self.t.FindGapFrom("172.16.0.0/12", 24)
    self.assertEqual(gap, "172.18.0.0/24")
    self.t.Insert("172.16.0.0/13", "findgapmiddling")
    self.t.Insert("172.24.0.0/13", "findgapmiddling")
    gap = self.t.FindGapFrom("172.16.0.0/12", 8)
    self.assertEqual(gap, None)
  
  def test_tree_find_gap_middling_occupied(self):
    node = self.t.Insert("172.16.0.0/12", "findgapmiddling", mark_used = False,
                         test_none = False)
    gap = self.t.FindGapFrom("172.16.0.0/12", 16)
    self.assertEqual(gap, "172.16.0.0/16")
    node.used = True
    gap = self.t.FindGapFrom("172.16.0.0/12", 16)
    self.assertEqual(gap, None)

  def test_tree_find_gap_from_complex(self):
    for count in range(4,12):
      total_route_set = []
      for route in self.t.GenerateForPrefix(count):
        total_route_set.append(route)
      picks = random.sample(total_route_set, count/2)
      for item in picks:
        obj1 = self.t.Insert(item, "complex_find_gap", mark_used = False)
      for item in total_route_set:
        if item in picks:
          gap = self.t.FindGapFrom(item, count)
          self.assertEqual(gap, item, "Find gap from gave [%s] not expected \
            [%s]" % (gap, item))
        else:
          gap = self.t.FindGapFrom(item, 24)
          self.assertEqual(gap, None)

class TreeIteration(unittest.TestCase):

  def setUp(self):
    self.t = tree.Tree()

  def test_tree_iterate_nodes(self):
    compare_list = []
    for item in self.t.GenerateForPrefix(3):
      obj1 = self.t.Insert(item, "testIterateNodes")
      compare_list.append(item)
    for node in self.t.IterateNodes():
      compare_list.remove(node)
    self.assertEqual(compare_list, [])

  def test_tree_only_supernets(self):
    #self.t.debug = 1
    #self.t.Insert('199.0.0.0/8', "walk prob root", mark_used = False)
    #self.assertEqual(self.t.Lookup('199.0.0.0/8').GetData(), "walk prob root")
    original_routes = ['199.4.32.0/19', '199.4.64.0/18', '199.4.128.0/24', '199.4.130.0/23',
                       '199.4.132.0/24', '199.4.134.0/23', '199.4.136.0/24', '199.4.139.0/24',
                       '199.4.140.0/24', '199.4.141.0/24']
    for route in original_routes:
      self.t.Insert(route, "walk problem", mark_used = True, propagate_used = True)
    result = []
    for f in self.t.IterateNodes(prefix='199.0.0.0/8', top_used=True):
      result.append(f)
    result2 = ['199.4.32.0/19', '199.4.64.0/18', '199.4.128.0/24', '199.4.130.0/23',
               '199.4.132.0/24', '199.4.134.0/23', '199.4.136.0/24', '199.4.139.0/24',
               '199.4.140.0/23']
    self.assertEqual(result, result2)

class TreeSlowTests(unittest.TestCase):

  def setUp(self):
    self.t = tree.Tree()

  def test_tree_slow_13_treeobj_find_gap_exhaust(self):
    self.t.Insert('0.0.0.0/8', "find_gap_exhaust")
    route = self.t.FindGap(8)
    while route != None:
      self.t.Insert(route, "find_gap_exhaust_extend")
      route = self.t.FindGap(8)

  def test_tree_slow_14_treeobj_find_gap_too_large(self):
    self.t.Insert('0.0.0.0/8', "find_gap_exhaust")
    route = self.t.FindGap(8)
    while route != None:
      self.t.Insert(route, "find_gap_exhaust_large")
      route = self.t.FindGap(7)

class TreeComparisonTests(unittest.TestCase):

  def setUp(self):
    self.t = tree.Tree()

  def test_compare_tree_1(self):
    self.t2 = tree.Tree()
    self.t.Insert('1.0.0.0/8', 'reason1')
    self.t2.Insert('1.0.0.0/8', 'reason2')
    self.assertEqual(self.t, self.t2)
    
  def test_compare_tree_2(self):
    self.t2 = tree.Tree()
    self.t.Insert('192.168.0.0/23', 'reason1', mark_used=True)
    self.t2.Insert('192.168.0.0/24', 'reason2', mark_used=True, propagate_used=True)
    self.t2.Insert('192.168.1.0/24', 'reason3', mark_used=True, propagate_used=True)
    #print "T2"
    #for x in self.t2.IterateNodes():
      #print "X T2", x
    #print "T1"
    #for y in self.t.IterateNodes():
      #print "Y T", y
    #print "ASSERT"
    self.assertEqual(self.t, self.t2)

  def test_compare_tree_3(self):
    pass
  
if __name__ == '__main__':
  unittest.main()
