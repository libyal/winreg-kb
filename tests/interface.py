#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry key and value collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake

from winregrc import interface

from tests import test_lib as shared_test_lib


class WindowsRegistryKeyCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key and value collector."""

  # pylint: disable=protected-access

  def testGetStringValueFromKey(self):
    """Tests the _GetStringValueFromKey function."""
    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = 'ValueData'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    value = collector._GetStringValueFromKey(
        registry_key, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'ValueData')

    value = collector._GetStringValueFromKey(
        None, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

    value = collector._GetStringValueFromKey(
        registry_key, 'Bogus', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = b'\x03\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    value = collector._GetStringValueFromKey(
        registry_key, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

  def testGetValueDataFromKey(self):
    """Tests the _GetValueDataFromKey function."""
    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = 'ValueData'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    value = collector._GetValueDataFromKey(registry_key, 'TestValue')
    self.assertEqual(value, value_data)

  def testGetValueFromKey(self):
    """Tests the _GetValueFromKey function."""
    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = 'ValueData'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    value = collector._GetValueFromKey(
        registry_key, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'ValueData')

    value = collector._GetValueFromKey(
        None, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

    value = collector._GetValueFromKey(
        registry_key, 'Bogus', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = b'\x03\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    value = collector._GetValueFromKey(
        registry_key, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 3)


if __name__ == '__main__':
  unittest.main()
