#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows application identifiers (AppID) collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import application_identifiers

from tests import test_lib as shared_test_lib


class ApplicationIdentifiersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows application identifiers (AppID) collector."""

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(
        '{fd6c8b29-e936-4a61-8da6-b0c12ad3ba00}')
    registry_file.AddKeyByPath('\\Classes\\AppID', registry_key)

    value_data = 'Wordpad'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = application_identifiers.ApplicationIdentifiersCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 1)

    application_identifier = test_results[0]
    self.assertIsNotNone(application_identifier)
    self.assertEqual(application_identifier.description, 'Wordpad')
    self.assertEqual(
        application_identifier.guid, '{fd6c8b29-e936-4a61-8da6-b0c12ad3ba00}')

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = application_identifiers.ApplicationIdentifiersCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)


if __name__ == '__main__':
  unittest.main()
