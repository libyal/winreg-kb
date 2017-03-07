#!/usr/bin/python
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

  def testGetValueAsStringFromKey(self):
    """Tests the _GetValueAsStringFromKey function."""
    collector = interface.WindowsRegistryKeyCollector()

    registry_key = dfwinreg_fake.FakeWinRegistryKey(u'TestKey')

    value_data = u'ValueData'.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'TestValue', data=value_data,
        data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    value = collector._GetValueAsStringFromKey(
        registry_key, u'TestValue', default_value=u'DefaultValue')
    self.assertEqual(value, u'ValueData')

    value = collector._GetValueAsStringFromKey(
        None, u'TestValue', default_value=u'DefaultValue')
    self.assertEqual(value, u'DefaultValue')

    value = collector._GetValueAsStringFromKey(
        registry_key, u'Bogus', default_value=u'DefaultValue')
    self.assertEqual(value, u'DefaultValue')


if __name__ == '__main__':
  unittest.main()
