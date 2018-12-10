#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Programs Cache information collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import registry as dfwinreg_registry

from winregrc import collector
from winregrc import errors
from winregrc import output_writers
from winregrc import programscache

from tests import test_lib


class TestOutputWriter(output_writers.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    text (list[str]): text.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.text = []

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text (str): text to write.
    """
    self.text.append(text)


class ProgramsCacheDataParserTest(test_lib.BaseTestCase):
  """Tests for the Programs Cache data parser."""

  def testParse(self):
    """Tests the Parse function."""
    data_parser = programscache.ProgramsCacheDataParser()

    with self.assertRaises(errors.ParseError):
      data_parser.Parse(b'')


class ProgramsCacheCollectorTest(test_lib.BaseTestCase):
  """Tests for the Programs Cache information collector."""

  @test_lib.skipUnlessHasTestFile(['NTUSER.DAT'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath(['NTUSER.DAT'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = programscache.ProgramsCacheCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry_collector.registry)
    self.assertTrue(result)

    test_output_writer.Close()

    # TODO: test program cache values.

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    test_output_writer = test_lib.TestOutputWriter()
    collector_object = programscache.ProgramsCacheCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertFalse(result)

    test_output_writer.Close()


if __name__ == '__main__':
  unittest.main()
