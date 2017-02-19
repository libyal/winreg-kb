#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the user profiles collector."""

import unittest

from winregrc import collector
from winregrc import output_writer
from winregrc import profiles

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


class UserProfilesCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows user profiles collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SOFTWARE'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'SOFTWARE'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = profiles.UserProfilesCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry_collector.registry, output_writer)

    # TODO: return user profile objects.
    self.assertNotEqual(output_writer.text, [])

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
