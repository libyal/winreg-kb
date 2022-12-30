#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows shell folders collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import shellfolders

from tests import test_lib as shared_test_lib


class ShellFoldersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows shell folders collector."""

  _GUID1 = '{2227a280-3aea-1069-a2de-08002b30309d}'
  _GUID2 = '{e7de9b1a-7533-4556-9484-b26fb486475e}'
  _LOCALIZED_STRING1 = '@%SystemRoot%\\system32\\prnfldr.dll,-8036'
  _NAME1 = 'Printers'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('CLSID')
    registry_file.AddKeyByPath('\\Classes', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID1)
    registry_key.AddSubkey(self._GUID1, subkey)

    shell_folder_key = dfwinreg_fake.FakeWinRegistryKey('ShellFolder')
    subkey.AddSubkey('ShellFolder', shell_folder_key)

    value_data = self._NAME1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._LOCALIZED_STRING1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'LocalizedString', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID2)
    registry_key.AddSubkey(self._GUID2, subkey)

    shell_folder_key = dfwinreg_fake.FakeWinRegistryKey('ShellFolder')
    subkey.AddSubkey('ShellFolder', shell_folder_key)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    test_results = sorted(
        collector_object.Collect(registry),
        key=lambda folder: folder.identifier)
    self.assertEqual(len(test_results), 2)

    shell_folder = test_results[0]
    self.assertIsNotNone(shell_folder)
    self.assertEqual(shell_folder.identifier, self._GUID1)
    self.assertEqual(shell_folder.name, self._NAME1)
    self.assertEqual(shell_folder.localized_string, self._LOCALIZED_STRING1)

    shell_folder = test_results[1]
    self.assertIsNotNone(shell_folder)
    self.assertEqual(shell_folder.identifier, self._GUID2)
    self.assertEqual(shell_folder.name, '')
    self.assertEqual(shell_folder.localized_string, '')

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)


if __name__ == '__main__':
  unittest.main()
