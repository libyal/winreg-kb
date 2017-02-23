#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the services collector."""

import unittest

from dfdatetime import filetime as dfdatetime_filetime
from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import collector
from winregrc import output_writer
from winregrc import services

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

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
    self.services.append(services)


class WindowsServicesCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the services collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SYSTEM'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'SYSTEM'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = services.WindowsServicesCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry_collector.registry, output_writer)

    self.assertNotEqual(output_writer.services, [])

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
