#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows Event Log providers collector."""

import unittest

from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry

from winregrc import eventlog_providers

from tests import test_lib as shared_test_lib


class EventLogProvidersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows Event Log providers collector."""

  def testCollect(self):
    """Tests the Collect function."""
    software_test_path = self._GetTestFilePath(['SOFTWARE'])
    self._SkipIfPathNotExists(software_test_path)

    system_test_path = self._GetTestFilePath(['SYSTEM'])
    self._SkipIfPathNotExists(system_test_path)

    registry = dfwinreg_registry.WinRegistry()

    with open(software_test_path, 'rb') as software_file_object:
      with open(system_test_path, 'rb') as system_file_object:
        registry_file = dfwinreg_regf.REGFWinRegistryFile(
            ascii_codepage='cp1252')
        registry_file.Open(software_file_object)

        key_path_prefix = registry.GetRegistryFileMapping(registry_file)
        registry_file.SetKeyPathPrefix(key_path_prefix)
        registry.MapFile(key_path_prefix, registry_file)

        registry_file = dfwinreg_regf.REGFWinRegistryFile(
            ascii_codepage='cp1252')
        registry_file.Open(system_file_object)

        key_path_prefix = registry.GetRegistryFileMapping(registry_file)
        registry_file.SetKeyPathPrefix(key_path_prefix)
        registry.MapFile(key_path_prefix, registry_file)

        collector_object = eventlog_providers.EventLogProvidersCollector()

        test_results = list(collector_object.Collect(registry))

    self.assertEqual(len(test_results), 974)

    eventlog_provider = test_results[0]
    self.assertEqual(eventlog_provider.identifier, '')
    self.assertEqual(eventlog_provider.log_sources, ['.NET Runtime'])
    self.assertEqual(eventlog_provider.log_type, 'Application')
    self.assertEqual(eventlog_provider.category_message_files, [])
    self.assertEqual(
        eventlog_provider.event_message_files,
        ['c:\\windows\\system32\\mscoree.dll'])
    self.assertEqual(eventlog_provider.parameter_message_files, [])

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = eventlog_providers.EventLogProvidersCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)


if __name__ == '__main__':
  unittest.main()
