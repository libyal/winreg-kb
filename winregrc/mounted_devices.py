# -*- coding: utf-8 -*-
"""Windows mounted devices collector."""

from dtfabric.runtime import data_maps as dtfabric_data_maps

from winregrc import data_format
from winregrc import errors


class MountedDevice(object):
  """Mounted device.

  Attributes:
    device (str): device.
    disk_identity (int): disk identity.
    identifier (str): identifier.
    partition_offset (int): partition offset.
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
    self.partition_offset = None


class MountedDevicesCollector(data_format.BinaryDataFormat):
  """Windows mounted devices collector."""

  _DEFINITION_FILE = 'mounted_devices.yaml'

  _MOUNTED_DEVICES_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\MountedDevices')

  def Collect(self, registry, output_writer):
    """Collects the mounted devices.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the mounted devices key was found, False if not.

    Raises:
      ParseError: if a mounted devices fixed-disk values could not be parsed.
    """
    mounted_devices_key = registry.GetKeyByPath(
        self._MOUNTED_DEVICES_KEY_PATH)
    if not mounted_devices_key:
      return False

    for registry_value in mounted_devices_key.GetValues():
      mounted_device = MountedDevice(registry_value.name)
      if len(registry_value.data) != 12:
        mounted_device.device = registry_value.data.decode('utf-16-le')
      else:
        data_type_map = self._GetDataTypeMap('mounted_devices_fixed_disk')

        context = dtfabric_data_maps.DataTypeMapContext(values={
            'data_size': len(registry_value.data)})

        try:
          fixed_disk_values = self._ReadStructureFromByteStream(
              registry_value.data, 0, data_type_map,
              'Mounted devices fixed-disk values', context=context)
        except (ValueError, errors.ParseError) as exception:
          raise errors.ParseError((
              'Unable to parse Mounted devices fixed-disk values with error: '
              '{0!s}').format(exception))

        mounted_device.disk_identity = fixed_disk_values.disk_identity
        mounted_device.partition_offset = fixed_disk_values.partition_offset

      output_writer.WriteMountedDevice(mounted_device)

    return True
