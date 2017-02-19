#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Task Cache information collector."""

import unittest

from winregrc import collector
from winregrc import output_writer
from winregrc import task_cache

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

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


class TaskCacheDataParserTest(shared_test_lib.BaseTestCase):
  """Tests for the Task Cache data parser."""

  # TODO: add tests.


class TaskCacheCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Task Cache information collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'NTUSER.DAT'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'NTUSER.DAT'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = task_cache.TaskCacheCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry_collector.registry, output_writer)

    # TODO: fix test.
    self.assertEqual(output_writer.text, [])

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
