#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract services information."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import services
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def __init__(self, use_tsv=False):
    """Initializes a stdout output writer.

    Args:
      use_tsv (bool): True if the output should in tab separated values.
    """
    super(StdoutWriter, self).__init__()
    self._printed_header = False
    self._use_tsv = use_tsv

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service (WindowsService): Windows service.
    """
    service_type_description = ''
    if service.service_type:
      service_type_description = service.GetServiceTypeDescription()

    start_value_description = ''
    if service.start_value is not None:
      start_value_description = service.GetStartValueDescription()

    if self._use_tsv:
      if not self._printed_header:
        print('\t'.join([
            'Service', 'Type', 'Display name', 'Description', 'Executable',
            'Start']))
        self._printed_header = True

      service_display_name = service.display_name or ''
      service_description = service.description or ''
      service_image_path = service.image_path or ''

      print('\t'.join([
          service.name, service_type_description, service_display_name,
          service_description, service_image_path, start_value_description]))

    else:
      print(f'{service.name:s}')

      if service.service_type:
        print(f'\tType\t\t\t: {service_type_description:s}')

      if service.display_name:
        print(f'\tDisplay name\t\t: {service.display_name:s}')

      if service.description:
        print(f'\tDescription\t\t: {service.description:s}')

      if service.image_path:
        print(f'\tExecutable\t\t: {service.image_path:s}')

      if service.object_name:
        object_name_description = service.GetObjectNameDescription()
        print(f'\t{object_name_description:s}\t\t: {service.object_name:s}')

      if service.start_value is not None:
        print(f'\tStart\t\t\t: {start_value_description:s}')

      print('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the services information from a SYSTEM Registry file.'))

  argument_parser.add_argument(
      '--all', dest='all_control_sets', action='store_true', default=False,
      help=(
          'Process all control sets instead of only the current control set.'))

  argument_parser.add_argument(
      '--diff', dest='diff_control_sets', action='store_true', default=False,
      help='Only list differences between control sets.')

  argument_parser.add_argument(
      '--tsv', dest='use_tsv', action='store_true', default=False,
      help='Use tab separated value (TSV) output.')

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

  collector_object = services.WindowsServicesCollector(debug=options.debug)

  output_writer_object = StdoutWriter(use_tsv=options.use_tsv)

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    if options.diff_control_sets:
      has_results = collector_object.Compare(
          scanner.registry, output_writer_object)

    else:
      has_results = False
      for windows_service in collector_object.Collect(
          scanner.registry, all_control_sets=options.all_control_sets):
        output_writer_object.WriteWindowsService(windows_service)
        has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No Services key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
