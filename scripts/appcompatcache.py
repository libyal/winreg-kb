#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Application Compatibility Cache information."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import appcompatcache
from winregrc import output_writers
from winregrc import volume_scanner


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Application Compatibility Cache information from '
      'a SYSTEM Registry file.'))

  argument_parser.add_argument(
      '--all', dest='all_control_sets', action='store_true', default=False,
      help=(
          'Process all control sets instead of only the current control set.'))

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
    print(('Unable to retrieve the volume with the Windows directory from: '
           '{0:s}.').format(options.source))
    print('')
    return False

  output_writer = output_writers.StdoutOutputWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    collector_object = appcompatcache.AppCompatCacheCollector(
        debug=options.debug, output_writer=output_writer)

    # TODO: change collector to generate AppCompatCacheCachedEntry
    has_results = collector_object.Collect(
        scanner.registry, all_control_sets=options.all_control_sets)
    if has_results:
      for cached_entry in collector_object.cached_entries:
        output_writer.WriteFiletimeValue(
            'Last modification time', cached_entry.last_modification_time)
        output_writer.WriteValue('Path', cached_entry.path)
        output_writer.WriteText('\n')

  finally:
    output_writer.Close()

  if not has_results:
    print('No application compatibility cache entries found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
