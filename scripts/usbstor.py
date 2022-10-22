#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract USB storage devices."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import usbstor
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  _PROPERTY_IDENTIFIERS_PER_SET = {
      '{540b947e-8b40-45bc-a8a2-6a0b894cbda2}': {
          '00000004': 'System.Devices.NumaNode'},
      '{83da6326-97a6-4088-9453-a1923f573b29}': {
          '00000006': 'System.Devices.SessionId',
          # DEVPKEY_Device_InstallDate
          '00000064': 'System.Devices.InstallDate',
          # DEVPKEY_Device_FirstInstallDate
          '00000065': 'System.Devices.FirstInstallDate',
          # DEVPKEY_Device_LastArrivalDate
          '00000066': 'System.Devices.LastArrivalDate',
          # DEVPKEY_Device_LastRemovalDate
          '00000067': 'System.Devices.LastRemovalDate'},
      '{a8b865dd-2e3d-4094-ad97-e593a70c75d6}': {
	      '00000002': 'System.Drivers.AssemblyDate',
          '00000003': 'System.Drivers.Version',
          '00000004': 'System.Drivers.Description',
          '00000005': 'System.Drivers.InfPath',
          '00000006': 'System.Drivers.InfSection',
          '00000007': 'System.Drivers.InfSectionExt',
          '00000008': 'System.Drivers.MatchingDeviceId',
          '00000009': 'System.Drivers.Provider',
          '0000000a': 'System.Drivers.PropPageProvider',
          '0000000b': 'System.Drivers.CoInstallers',
          '0000000c': 'System.Drivers.ResourcePickerTags',
          '0000000d': 'System.Drivers.ResourcePickerExceptions',
          '0000000e': 'System.Drivers.Rank',
          '0000000f': 'System.Drivers.LogoLevel'}}

  def WriteUserProfile(self, storage_device):
    """Writes an USB storage device to the output.

    Args:
      storage_device (UserProfile): USB storage device.
    """
    self.WriteText(f'Key path\t: {storage_device.key_path:s}\n')
    self.WriteText(f'Device type\t: {storage_device.device_type:s}\n')
    self.WriteText(f'Display name\t: {storage_device.display_name:s}\n')
    self.WriteText(f'Product\t\t: {storage_device.product:s}\n')

    if storage_device.revision:
      self.WriteText(f'Revision\t: {storage_device.revision:s}\n')

    if storage_device.vendor:
      self.WriteText(f'Vendor\t\t: {storage_device.vendor:s}\n')

    if storage_device.properties:
      self.WriteText('Properties:\n')
      for storage_device_property in storage_device.properties:
        self.WriteText((
            f'\t{storage_device_property.property_set:s} '
            f'{storage_device_property.identifier:s}'))

        description = self._PROPERTY_IDENTIFIERS_PER_SET.get(
            storage_device_property.property_set, {}).get(
                storage_device_property.identifier, None)
        if description:
          self.WriteText(f' ({description:s})')

        self.WriteText(f' (0x{storage_device_property.value_type:08x})')

        value = storage_device_property.value
        if storage_device_property.value_type == 0x00000007:
          self.WriteText(f': 0x{value:08x}\n')
        elif storage_device_property.value_type == 0x00000010:
          value = value.CopyToDateTimeStringISO8601()
          self.WriteText(f': {value:s}\n')
        else:
          self.WriteText(f': {value!s}\n')

    self.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the USB storage devices from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SYSTEM Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  if not scanner.ScanForWindowsVolume(
      options.source, options=volume_scanner_options):
    print((f'Unable to retrieve the volume with the Windows directory from: '
           f'{options.source:s}.'))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = usbstor.USBStorageDeviceCollector(debug=options.debug)

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    has_results = False
    for storage_device in collector_object.Collect(scanner.registry):
      output_writer_object.WriteUserProfile(storage_device)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No USB storage devices found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
