#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the Windows mounted devices collector."""

import unittest

from dfwinreg import definitions as dfwinreg_definitions
from dfwinreg import fake as dfwinreg_fake
from dfwinreg import registry as dfwinreg_registry

from winregrc import mounted_devices
from winregrc import output_writers

from tests import test_lib as shared_test_lib


class TestOutputWriter(output_writers.StdoutOutputWriter):
  """Output writer for testing.

  Attributes:
    mounted_devices (list[MountedDevice]): mounted devices.
  """

  def __init__(self):
    """Initializes an output writer object."""
    super(TestOutputWriter, self).__init__()
    self.mounted_devices = []

  def WriteMountedDevice(self, mounted_device):
    """Writes a mounted device to the output.

    Args:
      mounted_device (MountedDevice): a mounted device.
    """
    self.mounted_devices.append(mounted_device)


class MountedDevicesCollectorTest(shared_test_lib.BaseTestCase):
  """Tests for the Windows mounted devices collector."""

  def _CreateTestRegistry(self):
    """Creates Registry keys and values for testing.

    Returns:
      dfwinreg.WinRegistry: Windows Registry for testing.
    """
    key_path_prefix = 'HKEY_LOCAL_MACHINE\\System'

    registry_file = dfwinreg_fake.FakeWinRegistryFile(
        key_path_prefix=key_path_prefix)

    registry_key = dfwinreg_fake.FakeWinRegistryKey('MountedDevices')
    registry_file.AddKeyByPath('\\', registry_key)

    value_data = b'\x78\x56\x34\x12\x00\x10\x00\x00\x00\x00\x00\x00'
    registry_value = dfwinreg_fake.FakeWinRegistryValue(
        '\\DosDevices\\C:', data=value_data,
        data_type=dfwinreg_definitions.REG_BINARY)
    registry_key.AddValue(registry_value)

    registry_file.Open(None)

    registry = dfwinreg_registry.WinRegistry()
    registry.MapFile(key_path_prefix, registry_file)
    return registry

  def testCollect(self):
    """Tests the Collect function."""
    registry = self._CreateTestRegistry()

    collector_object = mounted_devices.MountedDevicesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.mounted_devices), 1)

    mounted_device = test_output_writer.mounted_devices[0]

    self.assertIsNotNone(mounted_device)
    self.assertEqual(mounted_device.identifier, '\\DosDevices\\C:')
    self.assertEqual(mounted_device.disk_identity, 0x12345678)
    self.assertEqual(mounted_device.partition_offset, 0x1000)

  def testCollectEmpty(self):
    """Tests the Collect function on an empty Registry."""
    registry = dfwinreg_registry.WinRegistry()

    collector_object = mounted_devices.MountedDevicesCollector()

    test_output_writer = TestOutputWriter()
    collector_object.Collect(registry, test_output_writer)
    test_output_writer.Close()

    self.assertEqual(len(test_output_writer.mounted_devices), 0)


if __name__ == '__main__':
  unittest.main()
