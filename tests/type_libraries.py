#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the type libraries collector."""

import unittest

from dfdatetime import filetime as dfdatetime_filetime
from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import collector
from winregrc import output_writer
from winregrc import type_libraries

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

  Attributes:
    type_libraries (list[TypeLibrary]): type libraries.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.type_libraries = []

  def WriteTypeLibrary(self, type_library):
    """Writes a type library folder to the output.

    Args:
      type_library (TypeLibrary): type library.
    """
    self.type_libraries.append(type_library)


class TypeLibraryCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the type libraries collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SOFTWARE'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'SOFTWARE'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = type_libraries.TypeLibrariesCollector()

    output_writer = TestOutputWriter()
    collector_object.Collect(registry_collector.registry, output_writer)
    output_writer.Close()

    self.assertNotEqual(output_writer.type_libraries, [])

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = type_libraries.TypeLibrariesCollector()

    output_writer = TestOutputWriter()
    collector_object.Collect(registry, output_writer)
    output_writer.Close()

    self.assertEqual(len(output_writer.type_libraries), 0)


if __name__ == '__main__':
  unittest.main()
