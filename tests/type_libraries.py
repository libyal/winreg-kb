#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the type libraries collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import type_libraries

from tests import test_lib


class TypeLibraryTest(test_lib.BaseTestCase):
  """Tests for the type library."""

  _DESCRIPTION = 'Microsoft Office List 14.0'
  _FILENAME = 'C:\\PROGRA~1\\MICROS~2\\Office14\\STSLIST.DLL'
  _IDENTIFIER = '{edcd5812-6a06-43c3-afac-46ef5d14e22c}'
  _VERSION = '3.0'

  def testInitialize(self):
    """Tests the initialize function."""
    type_library = type_libraries.TypeLibrary(
        self._IDENTIFIER, self._VERSION, self._DESCRIPTION, self._FILENAME)
    self.assertIsNotNone(type_library)


class TypeLibraryCollectorTest(test_lib.BaseTestCase):
  """Tests for the type libraries collector."""

  _DESCRIPTION1 = 'Microsoft Office List 14.0'
  _FILENAME1 = 'C:\\PROGRA~1\\MICROS~2\\Office14\\STSLIST.DLL'
  _IDENTIFIER1 = '{edcd5812-6a06-43c3-afac-46ef5d14e22c}'
  _VERSION1 = '3.0'

  _DESCRIPTION2 = 'IAS SDO Helper 1.0 Type Library'
  _FILENAME2 = '%SystemRoot%\\system32\\sdohlp.dll\\1'
  _IDENTIFIER2 = '{e9970f91-b6aa-11d9-b032-000d56c25c27}'
  _VERSION2 = '1.0'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._IDENTIFIER1)
    registry_file.AddKeyByPath('\\Classes\\TypeLib', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._VERSION1)
    registry_key.AddSubkey(self._VERSION1, subkey)

    value_data = self._DESCRIPTION1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    language_key = dfwinreg_fake.FakeWinRegistryKey('409')
    subkey.AddSubkey('409', language_key)

    platform_key = dfwinreg_fake.FakeWinRegistryKey('Win32')
    language_key.AddSubkey('Win32', platform_key)

    value_data = self._FILENAME1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    platform_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._IDENTIFIER2)
    registry_file.AddKeyByPath('\\Classes\\TypeLib', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._VERSION2)
    registry_key.AddSubkey(self._VERSION2, subkey)

    value_data = self._DESCRIPTION1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    language_key = dfwinreg_fake.FakeWinRegistryKey('0')
    subkey.AddSubkey('0', language_key)

    platform_key = dfwinreg_fake.FakeWinRegistryKey('x64')
    language_key.AddSubkey('x64', platform_key)

    value_data = self._FILENAME1.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    platform_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = type_libraries.TypeLibrariesCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertTrue(result)

    self.assertEqual(len(collector_object.type_libraries), 2)

    type_library = collector_object.type_libraries[0]

    self.assertIsNotNone(type_library)
    self.assertEqual(type_library.description, self._DESCRIPTION1)
    self.assertEqual(type_library.identifier, self._IDENTIFIER1)
    self.assertEqual(type_library.typelib_filename, self._FILENAME1)
    self.assertEqual(type_library.version, self._VERSION1)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = type_libraries.TypeLibrariesCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertFalse(result)

    self.assertEqual(len(collector_object.type_libraries), 0)


if __name__ == '__main__':
  unittest.main()
