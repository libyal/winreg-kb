#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the services collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writers
from winregrc import services

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writers.StdoutOutputWriter):
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

  _DESCRIPTION = '@%SystemRoot%\\System32\\wwansvc.dll,-258'
  _DISPLAY_NAME = '@%SystemRoot%\\System32\\wwansvc.dll,-257'
  _IMAGE_PATH = '%SystemRoot%\\system32\\svchost.exe -k LocalServiceNoNetwork'
  _OBJECT_NAME = 'NT Authority\\LocalService'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\System'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Select')
    registry_file.AddKeyByPath('\\', registry_key)

    value_data = b'\x01\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Current', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Services')
    registry_file.AddKeyByPath('\\ControlSet001', registry_key)

    subkey = dfwinreg_fake.FakeWinRegistryKey('WwanSvc')
    registry_key.AddSubkey('WwanSvc', subkey)

    value_data = self._DESCRIPTION.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Description', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._DISPLAY_NAME.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'DisplayName', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._IMAGE_PATH.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'ImagePath', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = self._OBJECT_NAME.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'ObjectName', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    subkey.AddValue(registry_value)

    value_data = b'\x03\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Start', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    subkey.AddValue(registry_value)

    value_data = b'\x20\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Type', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
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
