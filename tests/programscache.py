#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Programs Cache information collector."""

import unittest

from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry

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

  def testCollect(self):
    """Tests the Collect function."""
    test_path = self._GetTestFilePath(['NTUSER.DAT'])
    self._SkipIfPathNotExists(test_path)

    registry = dfwinreg_registry.WinRegistry()

    with open(test_path, 'rb') as file_object:
      registry_file = dfwinreg_regf.REGFWinRegistryFile(ascii_codepage='cp1252')
      registry_file.Open(file_object)

      key_path_prefix = registry.GetRegistryFileMapping(registry_file)
      registry_file.SetKeyPathPrefix(key_path_prefix)
      registry.MapFile(key_path_prefix, registry_file)

      test_output_writer = test_lib.TestOutputWriter()
      collector_object = programscache.ProgramsCacheCollector(
          output_writer=test_output_writer)

      result = collector_object.Collect(registry)

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
