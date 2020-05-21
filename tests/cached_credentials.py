#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the domain cached credentials collector."""

from __future__ import unicode_literals

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import cached_credentials
from winregrc import output_writers

from tests import test_lib


class TestOutputWriter(output_writers.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    cached_entries (list[AppCompatCacheCachedEntry]): Application Compatibility
        Cache cached entries.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.cached_entries = []

  def WriteCachedEntry(self, cached_entry):
    """Writes the Application Compatibility Cache cached entry to stdout.

    Args:
      cached_entry (AppCompatCacheCachedEntry): Application Compatibility
          Cache cached entry.
    """
    self.cached_entries.append(cached_entry)


class CachedCredentialsKeyCollectorTest(test_lib.BaseTestCase):
  """Tests for the Application Compatibility Cache collector."""

  # pylint: disable=protected-access

  _NL_KEY_MATERIAL_DATA = bytes(bytearray([
      0x48, 0x00, 0x00, 0x00, 0x48, 0x00, 0x00, 0x20, 0x9c, 0xc3, 0x0c, 0x00,
      0xc2, 0x0d, 0x08, 0x10, 0x9a, 0x04, 0x04, 0xbf, 0x14, 0x8b, 0xc7, 0xd0,
      0x0b, 0xe2, 0x9c, 0x40, 0x52, 0xa7, 0x8e, 0xaa, 0x01, 0x49, 0x25, 0x70,
      0x71, 0xdc, 0xa0, 0x69, 0x8e, 0x6c, 0x03, 0x1c, 0xb7, 0xdb, 0x19, 0x5c,
      0x8f, 0xf4, 0x11, 0xd1, 0x8d, 0x73, 0x07, 0xb0, 0x6f, 0x1a, 0xdb, 0x0b,
      0xee, 0xcb, 0x69, 0x7f, 0x73, 0x50, 0x24, 0x82, 0xf8, 0xe1, 0xa6, 0x27,
      0x97, 0xa9, 0xcc, 0x04, 0x8e, 0xe4, 0xca, 0xbb, 0x33, 0x68, 0x00, 0x7c]))

  _POLICY_ENCRYPTION_DATA = bytes(bytearray([
      0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
      0xfd, 0xd4, 0x3f, 0xb3, 0xee, 0x4f, 0xcd, 0x45, 0x2d, 0x02, 0xe8, 0x1e,
      0xf2, 0xac, 0xbd, 0x4f, 0xfc, 0x15, 0x12, 0x09, 0x0a, 0xb5, 0x48, 0x17,
      0x33, 0x8f, 0x42, 0x79, 0x8b, 0x89, 0x11, 0xd8, 0xec, 0x6e, 0x1c, 0xec,
      0x38, 0x5f, 0x27, 0xdf, 0x72, 0xca, 0x57, 0x96, 0x8d, 0x16, 0xd9, 0x37,
      0xc4, 0x14, 0x64, 0xd1, 0xa8, 0x47, 0x7a, 0xd4, 0x4b, 0xa3, 0x62, 0xd8,
      0xe7, 0x2b, 0xef, 0x76]))

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    registry = dfwinreg_registry.WinRegistry()

    key_path_prefix = 'HKEY_LOCAL_MACHINE\\Security'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Cache')
    registry_file.AddKeyByPath('\\', registry_key)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('PolSecretEncryptionKey')
    registry_file.AddKeyByPath('\\Policy', registry_key)

    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=self._POLICY_ENCRYPTION_DATA,
        data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('CurrVal')
    registry_file.AddKeyByPath('\\Policy\\Secrets\\NL$KM', registry_key)

    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '', data=self._NL_KEY_MATERIAL_DATA,
        data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)
    registry.MapFile(key_path_prefix, registry_file)

    key_path_prefix = 'HKEY_LOCAL_MACHINE\\System'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('Select')
    registry_file.AddKeyByPath('\\', registry_key)

    value_data = b'\x01\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        'Current', data=value_data, data_type=dfwinreg_definitions.REG_DWORD)
    registry_key.AddValue(registry_value)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(
        'Data', class_name='902a3f2c')
    registry_file.AddKeyByPath('\\ControlSet001\\Control\\Lsa', registry_key)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(
        'GBG', class_name='c0d054a4')
    registry_file.AddKeyByPath('\\ControlSet001\\Control\\Lsa', registry_key)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('JD', class_name='1ae33251')
    registry_file.AddKeyByPath('\\ControlSet001\\Control\\Lsa', registry_key)

    registry_key = dfwinreg_fake.FakeWinRegistryKey(
        'Skew1', class_name='be6a589c')
    registry_file.AddKeyByPath('\\ControlSet001\\Control\\Lsa', registry_key)

    registry_file.Open(None)
    registry.MapFile(key_path_prefix, registry_file)

    return registry

  def testGetBootKey(self):
    """Tests the _GetBootKey function."""
    registry = self._CreateTestRegistry()

    collector_object = cached_credentials.CachedCredentialsKeyCollector()

    boot_key = collector_object._GetBootKey(registry)
    self.assertEqual(boot_key, b'\xc0j\xbe2\xa4\xd0*Q\x1aX\xe3\x90?T,\x9c')

  def testGetLSAKey(self):
    """Tests the _GetLSAKey function."""
    registry = self._CreateTestRegistry()

    collector_object = cached_credentials.CachedCredentialsKeyCollector()

    lsa_key = collector_object._GetLSAKey(
        registry, b'\xc0j\xbe2\xa4\xd0*Q\x1aX\xe3\x90?T,\x9c')
    self.assertEqual(lsa_key, b'\x01\xd6]\xf4C\xaa\n\x86\xd9B\xd1\x174\xcef|')

  def testGetNLKey(self):
    """Tests the _GetNLKey function."""
    registry = self._CreateTestRegistry()

    collector_object = cached_credentials.CachedCredentialsKeyCollector()

    expected_nl_key = (
        b'\t\xfeDH\x1b5s\xb7;\x1d\xfc\xf7H\x9f\xc9`;`}\xcfb5P\xfd\xb5\xd8\x8f!u'
        b'\xec\x01\xe9\x85%\x96lhR\xc90\xfb\x1d\xb6\x9d\xcd\x8c\x14\x90\x91\xde'
        b'\xf1\xdd]\xd7d*\xce@\x97Z\xf1Yq ')

    nl_key = collector_object._GetNLKey(
        registry, b'\x01\xd6]\xf4C\xaa\n\x86\xd9B\xd1\x174\xcef|')
    self.assertEqual(nl_key, expected_nl_key)

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    test_output_writer = TestOutputWriter()
    collector_object = cached_credentials.CachedCredentialsKeyCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertTrue(result)

    test_output_writer.Close()

    # TODO:
    # self.assertEqual(len(collector_object.cached_entries), 1)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    test_output_writer = TestOutputWriter()
    collector_object = cached_credentials.CachedCredentialsKeyCollector(
        output_writer=test_output_writer)

    result = collector_object.Collect(registry)
    self.assertFalse(result)

    test_output_writer.Close()

    # TODO:
    # self.assertEqual(len(collector_object.cached_entries), 0)


if __name__ == '__main__':
  unittest.main()
