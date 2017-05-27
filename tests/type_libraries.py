#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the type libraries collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writer
from winregrc import type_libraries

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    type_libraries (list[TypeLibrary]): type libraries.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.type_libraries = []

  def WriteTypeLibrary(self, type_library):
    """Writes a type library folder to the output.

    Args:
      type_library (TypeLibrary): type library.
    """
    self.type_libraries.append(type_library)


class TypeLibraryTest(shared_test_lib.BaseTestCase):
  """Tests for the type library."""

  _DESCRIPTION = u'Microsoft Office List 14.0'
  _FILENAME = u'C:\\PROGRA~1\\MICROS~2\\Office14\\STSLIST.DLL'
  _GUID = u'{edcd5812-6a06-43c3-afac-46ef5d14e22c}'
  _VERSION = u'3.0'

  def testInitialize(self):
    """Tests the initialize function."""
    type_library = type_libraries.TypeLibrary(
        self._GUID, self._VERSION, self._DESCRIPTION, self._FILENAME)
    self.assertIsNotNone(type_library)


class TypeLibraryCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the type libraries collector."""

  _DESCRIPTION1 = u'Microsoft Office List 14.0'
  _FILENAME1 = u'C:\\PROGRA~1\\MICROS~2\\Office14\\STSLIST.DLL'
  _GUID1 = u'{edcd5812-6a06-43c3-afac-46ef5d14e22c}'
  _VERSION1 = u'3.0'

  _DESCRIPTION2 = u'IAS SDO Helper 1.0 Type Library'
  _FILENAME2 = u'%SystemRoot%\\system32\\sdohlp.dll\\1'
  _GUID2 = u'{e9970f91-b6aa-11d9-b032-000d56c25c27}'
  _VERSION2 = u'1.0'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._GUID1)
    registry_file.AddKeyByPath(u'\\Classes\\TypeLib', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._VERSION1)
    registry_key.AddSubkey(subkey)

    value_data = self._DESCRIPTION1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    language_key = dfwinreg_fake.FakeWinRegistryKey(u'409')
    subkey.AddSubkey(language_key)

    platform_key = dfwinreg_fake.FakeWinRegistryKey(u'Win32')
    language_key.AddSubkey(platform_key)

    value_data = self._FILENAME1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    platform_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._GUID2)
    registry_file.AddKeyByPath(u'\\Classes\\TypeLib', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(self._VERSION2)
    registry_key.AddSubkey(subkey)

    value_data = self._DESCRIPTION1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    language_key = dfwinreg_fake.FakeWinRegistryKey(u'0')
    subkey.AddSubkey(language_key)

    platform_key = dfwinreg_fake.FakeWinRegistryKey(u'x64')
    language_key.AddSubkey(platform_key)

    value_data = self._FILENAME1.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    platform_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = type_libraries.TypeLibrariesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.type_libraries), 2)

    type_library = test_output_writer.type_libraries[0]

    self.assertIsNotNone(type_library)
    self.assertEqual(type_library.description, self._DESCRIPTION1)
    self.assertEqual(type_library.guid, self._GUID1)
    self.assertEqual(type_library.typelib_filename, self._FILENAME1)
    self.assertEqual(type_library.version, self._VERSION1)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = type_libraries.TypeLibrariesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.type_libraries), 0)


if __name__ == '__main__':
  unittest.main()
