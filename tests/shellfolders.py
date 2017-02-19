#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows shell folders collector."""

import unittest

from winregrc import collector
from winregrc import output_writer
from winregrc import shellfolders

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writer.StdoutOutputWriter):
  """Class that defines a test output writer.

  Attributes:
    shell_folders (list[ShellFolder]): shell folders.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.shell_folders = []

  def WriteShellFolder(self, shell_folder):
    """Writes a shell folder to the output.

    Args:
      shell_folder (ShellFolder): a shell folder.
    """
    self.shell_folders.append(shell_folder)


class ShellFoldersCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows shell folders collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'SOFTWARE'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'SOFTWARE'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = shellfolders.ShellFoldersCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry_collector.registry, output_writer)

    self.assertNotEqual(output_writer.shell_folders, [])

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
