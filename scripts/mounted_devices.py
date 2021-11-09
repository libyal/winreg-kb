#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract mounted device information from the Windows Registry."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import collector
from winregrc import mounted_devices
from winregrc import output_writers


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteMountedDevice(self, mounted_device):
    """Writes a mounted device to the output.

    Args:
      mounted_device (MountedDevice): mounted device.
    """
    text = 'Identifier\t\t\t: {0:s}\n'.format(mounted_device.identifier)
    self.WriteText(text)

    if mounted_device.disk_identity:
      text = 'MBR disk identity\t\t: 0x{0:08x}\n'.format(
          mounted_device.disk_identity)
      self.WriteText(text)

      text = 'MBR dartition offset\t\t: {0:d} (0x{0:08x})\n'.format(
          mounted_device.partition_offset)
      self.WriteText(text)

    elif mounted_device.partition_identifier:
      text = 'GPT partition identifier\t: {0!s}\n'.format(
          mounted_device.partition_identifier)
      self.WriteText(text)

    elif mounted_device.device:
      text = 'Device\t\t\t\t: {0:s}\n'.format(mounted_device.device)
      self.WriteText(text)

    self.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts mounted device information from the Windows Registry.'))

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

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  mediator = collector.WindowsRegistryCollectorMediator()
  registry_collector = collector.WindowsRegistryCollector(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  if not registry_collector.ScanForWindowsVolume(
      options.source, options=volume_scanner_options):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  collector_object = mounted_devices.MountedDevicesCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No "MountedDevices" key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
