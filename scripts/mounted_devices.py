#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract Windows mounted devices."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import mounted_devices
from winregrc import output_writers
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteMountedDevice(self, mounted_device):
    """Writes a mounted device to the output.

    Args:
      mounted_device (MountedDevice): mounted device.
    """
    self.WriteText(f'Identifier\t\t\t: {mounted_device.identifier:s}\n')

    if mounted_device.disk_identity:
      self.WriteText(
          f'MBR disk identity\t\t: 0x{mounted_device.disk_identity:08x}\n')
      self.WriteText((
          f'MBR partition offset\t\t: {mounted_device.partition_offset:d} '
          f'(0x{mounted_device.partition_offset:08x})\n'))

    elif mounted_device.partition_identifier:
      self.WriteText((
          f'GPT partition identifier\t: '
          f'{mounted_device.partition_identifier!s}\n'))

    elif mounted_device.device:
      self.WriteText(f'Device\t\t\t\t: {mounted_device.device:s}\n')

    self.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Windows mounted devices from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SOFTWARE Registry file.'))

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

  collector_object = mounted_devices.MountedDevicesCollector(
      debug=options.debug)

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    has_results = False
    for mounted_device in collector_object.Collect(scanner.registry):
      output_writer_object.WriteMountedDevice(mounted_device)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No Windows mounted devices found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
