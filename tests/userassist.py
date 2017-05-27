#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Windows User Assist collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import output_writer
from winregrc import userassist

from tests import test_lib as shared_test_lib


_ENTRY_DATA_V3 = bytes(bytearray([
    0x01, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0xb0, 0xe3, 0x6e, 0x4b,
    0x17, 0x15, 0xca, 0x01]))

_ENTRY_DATA_V5 = bytes(bytearray([
    0x00, 0x00, 0x00, 0x00, 0x0c, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00,
    0x20, 0x30, 0x05, 0x00, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
    0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
    0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf,
    0x00, 0x00, 0x80, 0xbf, 0x00, 0x00, 0x80, 0xbf, 0xff, 0xff, 0xff, 0xff,
    0x04, 0xa8, 0x92, 0xd2, 0xab, 0x80, 0xcb, 0x01, 0x00, 0x00, 0x00, 0x00]))


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


class UserAssistDataParserTest(shared_test_lib.BaseTestCase):
  """Tests for the User Assist data parser."""

  def testParseEntry(self):
    """Tests the ParseEntry function."""
    data_parser = userassist.UserAssistDataParser()

    data_parser.ParseEntry(3, _ENTRY_DATA_V3)

    data_parser.ParseEntry(5, _ENTRY_DATA_V5)


class UserAssistCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows User Assist collector."""

  _GUID = u'{5E6AB780-7743-11CF-A12B-00AA004AE837}'

  _UEME_CTLSESSION_VALUE_DATA = bytes(bytearray([
      0xb0, 0xa8, 0x50, 0x0e, 0x01, 0x00, 0x00, 0x00]))

  _ENTRY_VALUE_DATA = bytes(bytearray([
      0x01, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x54, 0x4b, 0xf6, 0xd3,
      0x15, 0x15, 0xca, 0x01]))

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_CURRENT_USER'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._GUID)
    registry_file.AddKeyByPath(
        u'\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist',
        registry_key)

    value_data = b'\x03\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Version', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    subkey = dfwinreg_fake.FakeWinRegistryKey(u'Count')
    registry_key.AddSubkey(subkey)

    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'HRZR_PGYFRFFVBA', data=self._UEME_CTLSESSION_VALUE_DATA,
        data_type=dfwinreg_definitions.REG_BINARY)
    subkey.AddValue(registry_value)

    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'HRZR_EHACVQY:%pfvqy2%\\Jvaqbjf Zrffratre.yax',
        data=self._ENTRY_VALUE_DATA, data_type=dfwinreg_definitions.REG_BINARY)
    subkey.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = userassist.UserAssistCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    # TODO: return user assist objects.
    self.assertEqual(len(test_output_writer.text), 0)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = userassist.UserAssistCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.text), 0)


if __name__ == '__main__':
  unittest.main()
