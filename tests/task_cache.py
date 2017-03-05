#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the Task Cache information collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

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

  _DYNAMIC_INFO_DATA = b''.join(map(chr, [
      0x03, 0x00, 0x00, 0x00, 0x0c, 0x1c, 0x7d, 0x12, 0x3f, 0x04, 0xca, 0x01,
      0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0x00, 0x00, 0x00, 0x00]))

  _GUID = u'{8905ECD8-016F-4DC2-90E6-A5F1FA6A841A}'

  _PATH = (
      u'\\Microsoft\\Windows\\Active Directory Rights Management Services '
      u'Client\\AD RMS Rights Policy Template Management (Automated)')

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(self._GUID)
    registry_file.AddKeyByPath(
        u'\\Microsoft\\Windows NT\\CurrentVersion\\Schedule\\TaskCache\\Tasks',
        registry_key)

    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'DynamicInfo', data=self._DYNAMIC_INFO_DATA,
        data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    value_data = self._PATH.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Path', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(
        u'AD RMS Rights Policy Template Management (Automated)')
    registry_file.AddKeyByPath((
        u'\\Microsoft\\Windows NT\\CurrentVersion\\Schedule\\TaskCache\\Tree\\'
        u'Microsoft\\Windows\\Active Directory Rights Management Services '
        u'Client'), registry_key)

    value_data = u'{8905ECD8-016F-4DC2-90E6-A5F1FA6A841A}\x00'.encode(
        u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'Id', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = task_cache.TaskCacheCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    # TODO: return task cache objects.
    self.assertEqual(len(test_output_writer.text), 4)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = task_cache.TaskCacheCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.text), 0)


if __name__ == '__main__':
  unittest.main()
