#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Programs Cache information collector."""

import unittest

from dfwinreg import registry as dfwinreg_registry

from winregrc import collector
from winregrc import errors
from winregrc import output_writer
from winregrc import programscache

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
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
      text: the text to write.
    """
    self.text.append(text)


class ProgramsCacheDataParserTest(shared_test_lib.BaseTestCase):
  """Tests for the Programs Cache data parser."""

  def testParse(self):
    """Tests the Parse function."""
    data_parser = programscache.ProgramsCacheDataParser()

    with self.assertRaises(errors.ParseError):
      data_parser.Parse(b'')


class ProgramsCacheCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Programs Cache information collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'NTUSER.DAT'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'NTUSER.DAT'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = programscache.ProgramsCacheCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry_collector.registry, test_output_writer)
    test_output_writer.Close()

    # TODO: fix test.
    self.assertEqual(test_output_writer.text, [])

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = programscache.ProgramsCacheCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.text), 0)


if __name__ == '__main__':
  unittest.main()
