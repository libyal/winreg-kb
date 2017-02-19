#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Application Compatibility Cache collector."""

import unittest

from winregrc import appcompatcache

from tests import test_lib as shared_test_lib


class TestOutputWriter(object):
  """Class that defines a test output writer.

  Attributes:
    known_folders (list[KnownFolder]): known folders.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.known_folders = []

  def Close(self):
    """Closes the output writer object."""
    return

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder (KnownFolder): a known folder.
    """
    self.known_folders.append(known_folder)


class AppCompatCacheCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Application Compatibility Cache collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SYSTEM'])
  def testCollect(self):
    """Tests the Collect function."""
    test_path = u''
    output_writer = TestOutputWriter()

    collector_object = appcompatcache.AppCompatCacheCollector()
    collector_object.GetWindowsVolumePathSpec(test_path)
    collector_object.Collect(output_writer)
    collector_object.Close()


if __name__ == '__main__':
  unittest.main()
