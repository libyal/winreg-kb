#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract system information."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import sysinfo
from winregrc import volume_scanner


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the system information from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False, help=(
          'enable debug output.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
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

  output_writer = output_writers.StdoutOutputWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
    print('')
    return False

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
  collector_object = sysinfo.SystemInfoCollector(
      debug=options.debug, output_writer=output_writer)

  result = collector_object.Collect(scanner.registry)
  if not result:
    print('No Current Version key found.')
  else:
    output_writer.WriteValue(
        'Product name', collector_object.system_information.product_name)
    output_writer.WriteValue(
        'Product identifier',
        collector_object.system_information.product_identifier)

    output_writer.WriteValue(
        'Current version', collector_object.system_information.current_version)
    output_writer.WriteValue(
        'Current type', collector_object.system_information.current_type)
    output_writer.WriteValue(
        'Current build number',
        collector_object.system_information.current_build_number)
    output_writer.WriteValue(
        'CSD version', collector_object.system_information.csd_version)

    output_writer.WriteValue(
        'Registered organization',
        collector_object.system_information.registered_organization)
    output_writer.WriteValue(
        'Registered owner',
        collector_object.system_information.registered_owner)

    date_time_value = collector_object.system_information.installation_date
    date_time_string = date_time_value.CopyToDateTimeString()
    output_writer.WriteValue('Installation date', date_time_string)

    output_writer.WriteValue(
        'Path name', collector_object.system_information.path_name)
    output_writer.WriteValue(
        '%SystemRoot%', collector_object.system_information.system_root)

    output_writer.WriteText('\n')

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
