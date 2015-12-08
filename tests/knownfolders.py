#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows known folders collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake

from winreg_kb import knownfolders


class TestOutputWriter(object):
  """Class that defines a test output writer.

  Attributes:
    known_folders: a list of known folders.
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
      A boolean containing True if successful or False if not.
    """
    return True

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder: a known folder (instance KnownFolder).
    """
    self.known_folders.append(known_folder)


class KnownFoldersCollectorTest(unittest.TestCase):
  """Tests for the Windows known folders collector."""

  def testCollect(self):
    """Tests the Collect function."""
    test_path = u''
    output_writer = TestOutputWriter()

    collector_object = knownfolders.KnownFoldersCollector()
    collector_object.GetWindowsVolumePathSpec(test_path)
    collector_object.Collect(output_writer)
    collector_object.Close()


if __name__ == '__main__':
  unittest.main()
