#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry key and value filters."""

from __future__ import unicode_literals

import unittest

from winregrc import filters

from tests import test_lib as shared_test_lib


class WindowsRegistryKeyPathFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathFilter('test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for key_paths.
  # TODO: add test for Match.


class WindowsRegistryKeyPathPrefixFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path prefix filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathPrefixFilter('test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


class WindowsRegistryKeyPathSuffixFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key path suffix filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyPathSuffixFilter('test')
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


class WindowsRegistryKeyWithValuesFilterTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key with values filter."""

  def testInitialize(self):
    """Tests the initialize function."""
    test_filter = filters.WindowsRegistryKeyWithValuesFilter(['test'])
    self.assertIsNotNone(test_filter)

  # TODO: add test for Match.


if __name__ == '__main__':
  unittest.main()
