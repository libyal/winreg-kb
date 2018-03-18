#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows Registry key and value collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake

from winregrc import interface

from tests import test_lib as shared_test_lib


class WindowsRegistryKeyCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Registry key and value collector."""

  # pylint: disable=protected-access

  def testGetValueAsStringFromKey(self):
    """Tests the _GetValueAsStringFromKey function."""
    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey('TestKey')

    value_data = 'ValueData'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    value = collector._GetValueAsStringFromKey(
        registry_key, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'ValueData')

    value = collector._GetValueAsStringFromKey(
        None, 'TestValue', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')

    value = collector._GetValueAsStringFromKey(
        registry_key, 'Bogus', default_value='DefaultValue')
    self.assertEqual(value, 'DefaultValue')


if __name__ == '__main__':
  unittest.main()
