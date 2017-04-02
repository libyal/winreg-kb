#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry key and value filters."""

import unittest

from winregrc import filters

from tests import test_lib as shared_test_lib


class WindowsRegistryKeyPathFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathFilter(u'test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for key_paths.
  # TODO: add test for Match.


class WindowsRegistryKeyPathPrefixFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path prefix filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathPrefixFilter(u'test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


class WindowsRegistryKeyPathSuffixFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path suffix filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathSuffixFilter(u'test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


class WindowsRegistryKeyWithValuesFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key with values filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyWithValuesFilter([u'test'])
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


if __name__ == '__main__':
  unittest.main()
