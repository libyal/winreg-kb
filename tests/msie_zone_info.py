#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Microsoft Internet Explorer (MSIE) zone collector."""

import unittest

from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry

from winregrc import msie_zone_info

from tests import test_lib as shared_test_lib


class MSIEZoneInformationCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Microsoft Internet Explorer (MSIE) zone collector."""

  def testCollect(self):
    """Tests the Collect function."""
    test_path = self._GetTestFilePath(['SOFTWARE'])
    self._SkipIfPathNotExists(test_path)

    registry = dfwinreg_registry.WinRegistry()

    with open(test_path, 'rb') as file_object:
      registry_file = dfwinreg_regf.REGFWinRegistryFile(ascii_codepage='cp1252')
      registry_file.Open(file_object)

      key_path_prefix = registry.GetRegistryFileMapping(registry_file)
      registry_file.SetKeyPathPrefix(key_path_prefix)
      registry.MapFile(key_path_prefix, registry_file)

      collector_object = msie_zone_info.MSIEZoneInformationCollector()

      test_results = list(collector_object.Collect(registry))

    self.assertEqual(len(test_results), 1724)

    zone_information = test_results[0]
    self.assertEqual(zone_information.zone, '0')
    self.assertEqual(zone_information.zone_name, 'Computer')
    self.assertEqual(zone_information.control, '1809')
    self.assertEqual(zone_information.control_value, 3)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = msie_zone_info.MSIEZoneInformationCollector()

    test_results = list(collector_object.Collect(registry))
    self.assertEqual(len(test_results), 0)


if __name__ == '__main__':
  unittest.main()
