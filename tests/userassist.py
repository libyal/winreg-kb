#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows User Assist collector."""

import unittest

from winregrc import collector
from winregrc import output_writer
from winregrc import userassist

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


class UserAssistDataParserTest(shared_test_lib.BaseTestCase):
  """Tests for the User Assist data parser."""

  _ENTRY_DATA_V3 = b''.join(map(chr, [
      0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0xb0, 0xe3, 0x6e, 0x4b,
      0x17, 0x15, 0xca, 0x01]))

  _ENTRY_DATA_V5 = b''.join(map(chr, [
      0x00, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00,
      0x20, 0x30, 0x05, 0x00, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
      0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
      0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
      0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0xff, 0xff, 0xff, 0xff,
      0x04, 0xa8, 0x92, 0xd2, 0xab, 0x80, 0xcb, 0x01, 0x00, 0x00, 0x00, 0x00]))

  # TODO: add tests.


class UserAssistCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows User Assist collector."""

  @shared_test_lib.skipUnlessHasTestFile([u'NTUSER.DAT'])
  def testCollect(self):
    """Tests the Collect function."""
    registry_collector = collector.WindowsRegistryCollector()

    test_path = self._GetTestFilePath([u'NTUSER.DAT'])
    registry_collector.ScanForWindowsVolume(test_path)

    self.assertIsNotNone(registry_collector.registry)

    collector_object = userassist.UserAssistCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry_collector.registry, output_writer)

    # TODO: fix test.
    self.assertEqual(output_writer.text, [])

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
