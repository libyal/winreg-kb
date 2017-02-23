#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the system information collector."""

import unittest

from dfdatetime import filetime as dfdatetime_filetime
from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import collector
from winregrc import output_writer
from winregrc import sysinfo

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


class SystemInfoCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the system information collector."""

  _CSD_VERSION = u'Service Pack 1'
  _CURRENT_BUILD_NUMBER = u'7601'
  _CURRENT_TYPE = u'Multiprocessor Free'
  _CURRENT_VERSION = u'6.1'
  _INSTALLATION_DATE = 1289406535
  _PATH_NAME = u'C:\Windows'
  _PRODUCT_IDENTIFIER = u'00426-067-1817155-86250'
  _PRODUCT_NAME = u'Windows 7 Ultimate'
  _REGISTERED_ORGANIZATION = u''
  _REGISTERED_OWNER = u'Windows User'
  _SYSTEM_ROOT = u'C:\Windows'

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = u'HKEY_LOCAL_MACHINE\\Software'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(u'CurrentVersion')
    registry_file.AddKeyByPath(u'\\Microsoft\\Windows NT', registry_key)

    value_data = self._PRODUCT_NAME.encode(u'utf-16-le')
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        u'ProductName', data=value_data, data_type=dfwinreg_definitions.REG_SZ)
    registry_key.AddValue(registry_value)

    # TODO: add more values.

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = sysinfo.SystemInfoCollector()
    output_writer = TestOutputWriter()

    collector_object.Collect(registry, output_writer)

    # TODO: return system information objects.
    self.assertEqual(len(output_writer.text), 10)

    output_writer.Close()


if __name__ == '__main__':
  unittest.main()
