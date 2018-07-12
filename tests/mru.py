#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Most Recently Used (MRU) collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import mru

from tests import test_lib


class MostRecentlyUsedCollectorTest(test_lib.BaseTestCase):
  """Tests for the Most Recently Used (MRU) collector."""

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_CURRENT_USER'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('RecentDocs')
    registry_file.AddKeyByPath(
        '\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer',
        registry_key)

    value_data = b'a\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'MRUList', data=value_data, data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    value_data = 'MyFile.txt\x00'.encode('utf_16_le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'a', data=value_data, data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = mru.MostRecentlyUsedCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertTrue(result)

    test_output_writer.Close()

    self.assertEqual(len(collector_object.mru_entries), 1)

    mru_entry = collector_object.mru_entries[0]
    self.assertIsNotNone(mru_entry)
    self.assertEqual(mru_entry.string, 'MyFile.txt')

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = mru.MostRecentlyUsedCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertFalse(result)

    test_output_writer.Close()

    self.assertEqual(len(collector_object.mru_entries), 0)


if __name__ == '__main__':
  unittest.main()
