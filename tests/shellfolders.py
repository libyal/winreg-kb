#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows shell folders collector."""

import unittest

from dfdatetime import filetime as dfdatetime_filetime
from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writer
from winregrc import shellfolders

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

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

  _GUID = u'{2227a280-3aea-1069-a2de-08002b30309d}'
  _LOCALIZED_STRING = u'@%SystemRoot%\system32\prnfldr.dll,-8036'
  _NAME = u'Printers'

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

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID)
    registry_key.AddSubkey(subkey)

    shell_folder_key = dfwinreg_fake.FakeWinRegistryKey(u'ShellFolder')
    subkey.AddSubkey(shell_folder_key)

    value_data = self._NAME.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._LOCALIZED_STRING.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'LocalizedString', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    output_writer = TestOutputWriter()
    collector_object.Collect(registry, output_writer)
    output_writer.Close()

    self.assertEqual(len(output_writer.shell_folders), 1)

    shell_folder = output_writer.shell_folders[0]

    self.assertIsNotNone(shell_folder)
    self.assertEqual(shell_folder.guid, self._GUID)
    self.assertEqual(shell_folder.name, self._NAME)
    self.assertEqual(shell_folder.localized_string, self._LOCALIZED_STRING)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = shellfolders.ShellFoldersCollector()

    output_writer = TestOutputWriter()
    collector_object.Collect(registry, output_writer)
    output_writer.Close()

    self.assertEqual(len(output_writer.shell_folders), 0)


if __name__ == '__main__':
  unittest.main()
