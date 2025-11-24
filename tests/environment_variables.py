#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the environment variables collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import environment_variables

from tests import test_lib as shared_test_lib


class EnvironmentVariablesCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the environment variables collector."""

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\System'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Environment')
    registry_file.AddKeyByPath(
        '\\CurrentControlSet\\Control\\Session Manager', registry_key)

    value_data = '%SystemRoot%\\TEMP'.encode('utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'TEMP', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = environment_variables.EnvironmentVariablesCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 1)

    environment_variable = test_results[0]
    self.assertIsNotNone(environment_variable)
    self.assertEqual(environment_variable.name, '%TEMP%')
    self.assertEqual(environment_variable.value, '%SystemRoot%\\TEMP')

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = environment_variables.EnvironmentVariablesCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)


if __name__ == '__main__':
  unittest.main()
