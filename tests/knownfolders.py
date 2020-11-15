#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows known folders collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import knownfolders
from winregrc import output_writers

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writers.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    known_folders (list[KnownFolder]): known folders.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.known_folders = []

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder (KnownFolder): a known folder.
    """
    self.known_folders.append(known_folder)


class KnownFoldersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows known folders collector."""

  _GUID = '374de290-123f-4565-9164-39c4925e467b'
  _LOCALIZED_NAME = '@%SystemRoot%\\system32\\shell32.dll,-21798'
  _NAME = 'Downloads'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('FolderDescriptions')
    registry_file.AddKeyByPath(
        '\\Microsoft\\Windows\\CurrentVersion\\Explorer', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._GUID)
    registry_key.AddSubkey(self._GUID, subkey)

    value_data = self._NAME.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Name', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._LOCALIZED_NAME.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'LocalizedName', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = knownfolders.KnownFoldersCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.known_folders), 1)

    known_folder = test_output_writer.known_folders[0]

    self.assertIsNotNone(known_folder)
    self.assertEqual(known_folder.guid, self._GUID)
    self.assertEqual(known_folder.name, self._NAME)
    self.assertEqual(known_folder.localized_name, self._LOCALIZED_NAME)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = knownfolders.KnownFoldersCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.known_folders), 0)


if __name__ == '__main__':
  unittest.main()
