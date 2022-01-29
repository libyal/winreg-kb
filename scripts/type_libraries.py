#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract type libraries."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import type_libraries
from winregrc import volume_scanner


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the type libraries from the Windows Registry.'))

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
    print(('Unable to retrieve the volume with the Windows directory from: '
           '{0:s}.').format(options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = type_libraries.TypeLibrariesCollector(
      debug=options.debug, output_writer=output_writer)

  result = collector_object.Collect(scanner.registry)
  if not result:
    print('No TypeLib key found.')
  else:
    for type_library in collector_object.type_libraries:
      print('{0:s}\t{1:s}\t{2:s}\t{3:s}'.format(
          type_library.guid, type_library.version, type_library.description,
          type_library.typelib_filename))

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
