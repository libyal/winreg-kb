#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows known folders collector."""

import unittest

from winregrc import knownfolders
from winregrc import output_writer

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

  Attributes:
    known_folders (list[KnownFolder]): known folders.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.known_folders = []

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder (KnownFolder): a known folder.
    """
    self.known_folders.append(known_folder)


class KnownFoldersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows known folders collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SOFTWARE'])
  def testCollect(self):
    """Tests the Collect function."""
    collector_object = knownfolders.KnownFoldersCollector()

    test_path = self._GetTestFilePath([u'SOFTWARE'])
    collector_object.ScanForWindowsVolume(test_path)

    output_writer = TestOutputWriter()
    collector_object.Collect(output_writer)

    self.assertNotEqual(output_writer.known_folders, [])


if __name__ == '__main__':
  unittest.main()
