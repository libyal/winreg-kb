#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows shell folders collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writer
from winregrc import shellfolders

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    shell_folders (list[ShellFolder]): shell folders.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.shell_folders = []

  def WriteShellFolder(self, shell_folder):
    """Writes a shell folder to the output.

    Args:
      shell_folder (ShellFolder): a shell folder.
    """
    self.shell_folders.append(shell_folder)


class ShellFoldersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows shell folders collector."""

  _GUID1 = u'{2227a280-3aea-1069-a2de-08002b30309d}'
  _GUID2 = u'{e7de9b1a-7533-4556-9484-b26fb486475e}'
  _LOCALIZED_STRING1 = u'@%SystemRoot%\\system32\\prnfldr.dll,-8036'
  _NAME1 = u'Printers'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(u'CLSID')
    registry_file.AddKeyByPath(u'\\Classes', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID1)
    registry_key.AddSubkey(subkey)

    shell_folder_key = dfwinreg_fake.FakeWinRegistryKey(u'ShellFolder')
    subkey.AddSubkey(shell_folder_key)

    value_data = self._NAME1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._LOCALIZED_STRING1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'LocalizedString', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID2)
    registry_key.AddSubkey(subkey)

    shell_folder_key = dfwinreg_fake.FakeWinRegistryKey(u'ShellFolder')
    subkey.AddSubkey(shell_folder_key)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.shell_folders), 2)

    shell_folders = sorted(
        test_output_writer.shell_folders, key=lambda folder: folder.guid)

    shell_folder = shell_folders[0]

    self.assertIsNotNone(shell_folder)
    self.assertEqual(shell_folder.guid, self._GUID1)
    self.assertEqual(shell_folder.name, self._NAME1)
    self.assertEqual(shell_folder.localized_string, self._LOCALIZED_STRING1)

    shell_folder = shell_folders[1]

    self.assertIsNotNone(shell_folder)
    self.assertEqual(shell_folder.guid, self._GUID2)
    self.assertEqual(shell_folder.name, u'')
    self.assertEqual(shell_folder.localized_string, u'')

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.shell_folders), 0)


if __name__ == '__main__':
  unittest.main()
