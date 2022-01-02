#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the services collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import services

from tests import test_lib as shared_test_lib


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

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Services')
    registry_file.AddKeyByPath('\\CurrentControlSet', registry_key)

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

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 1)

    windows_service = test_results[0]
    self.assertIsNotNone(windows_service)
    self.assertEqual(windows_service.description, self._DESCRIPTION)
    self.assertEqual(windows_service.display_name, self._DISPLAY_NAME)
    self.assertEqual(windows_service.image_path, self._IMAGE_PATH)
    self.assertEqual(windows_service.name, 'WwanSvc')
    self.assertEqual(windows_service.object_name, self._OBJECT_NAME)
    self.assertEqual(windows_service.service_type, 32)
    self.assertEqual(windows_service.start_value, 3)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = services.WindowsServicesCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)

  # TODO: add tests for Compare method


if __name__ == '__main__':
  unittest.main()
