# -*- coding: utf-8 -*-
"""Windows mounted devices collector."""

from winregrc import data_format
from winregrc import errors


class MountedDevice(object):
  """Mounted device.

  Attributes:
    device (str): device.
    disk_identity (int): MBR disk identity.
    identifier (str): identifier.
    partition_identifier (str): GPT partition identifier.
    partition_offset (int): MBR partition offset.
  """

  def __init__(self, identifier):
    """Initializes a mounted device.

    Args:
      identifier (str): identifier.
    """
    super(MountedDevice, self).__init__()
    self.device = None
    self.disk_identity = None
    self.identifier = identifier
    self.partition_identifier = None
    self.partition_offset = None


class MountedDevicesCollector(data_format.BinaryDataFormat):
  """Windows mounted devices collector."""

  _DEFINITION_FILE = 'mounted_devices.yaml'

  _MOUNTED_DEVICES_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\MountedDevices')

  def _ParseValue(self, registry_value):
    """Parses a mounted devices Windows Registry value.

    Args:
      registry (dfwinreg.WinRegistryValue): a mounted devices Windows Registry
          value.

    Returns:
      MountedDevice: a mounted device attribute container.

    Raises:
      ParseError: if the value could not be parsed.
    """
    mounted_device = MountedDevice(registry_value.name)
    value_data_size = len(registry_value.data)

    if value_data_size == 12:
      data_type_map = self._GetDataTypeMap('mounted_devices_mbr_partition')

      try:
        partition_values = self._ReadStructureFromByteStream(
            registry_value.data, 0, data_type_map,
            'Mounted devices MBR partition values')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to parse Mounted devices MBR partition values with '
            'error: {0!s}').format(exception))

      mounted_device.disk_identity = partition_values.disk_identity
      mounted_device.partition_offset = partition_values.partition_offset

    elif value_data_size == 24:
      data_type_map = self._GetDataTypeMap('mounted_devices_gpt_partition')

      try:
        partition_values = self._ReadStructureFromByteStream(
            registry_value.data, 0, data_type_map,
            'Mounted devices GPT partition values')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to parse Mounted devices GPT partition values with '
            'error: {0!s}').format(exception))

      mounted_device.partition_identifier = (
          partition_values.partition_identifier)

    else:
      mounted_device.device = registry_value.data.decode('utf-16-le')

    return mounted_device

  def Collect(self, registry, output_writer):
    """Collects the mounted devices.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the mounted devices key was found, False if not.

    Raises:
      ParseError: if a mounted devices value could not be parsed.
    """
    mounted_devices_key = registry.GetKeyByPath(
        self._MOUNTED_DEVICES_KEY_PATH)
    if not mounted_devices_key:
      return False

    for registry_value in mounted_devices_key.GetValues():
      mounted_device = self._ParseValue(registry_value)
      output_writer.WriteMountedDevice(mounted_device)

    return True
