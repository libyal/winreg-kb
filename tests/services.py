#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the services collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writer
from winregrc import services

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    services (list[WindowsService]): services.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.services = []

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service (WindowsService): Windows service.
    """
    self.services.append(service)


class WindowsServicesCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the services collector."""

  _DESCRIPTION = u'@%SystemRoot%\\System32\\wwansvc.dll,-258'
  _DISPLAY_NAME = u'@%SystemRoot%\\System32\\wwansvc.dll,-257'
  _IMAGE_PATH = u'%SystemRoot%\\system32\\svchost.exe -k LocalServiceNoNetwork'
  _OBJECT_NAME = u'NT Authority\\LocalService'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_LOCAL_MACHINE\\System'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(u'Select')
    registry_file.AddKeyByPath(u'\\', registry_key)

    value_data = b'\x01\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Current', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(u'Services')
    registry_file.AddKeyByPath(u'\\ControlSet001', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey(u'WwanSvc')
    registry_key.AddSubkey(subkey)

    value_data = self._DESCRIPTION.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Description', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._DISPLAY_NAME.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'DisplayName', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._IMAGE_PATH.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'ImagePath', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._OBJECT_NAME.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'ObjectName', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = b'\x03\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Start', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    subkey.AddValue(registry_value)

    value_data = b'\x20\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Type', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    subkey.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = services.WindowsServicesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(
        registry, test_output_writer, all_control_sets=True)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.services), 1)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = services.WindowsServicesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.services), 0)


if __name__ == '__main__':
  unittest.main()
