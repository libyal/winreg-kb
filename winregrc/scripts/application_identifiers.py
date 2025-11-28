#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract Windows application identifiers (AppID)."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import application_identifiers
from winregrc import output_writers
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteApplicationIdentifier(self, application_identifier):
    """Writes an application identifier to the output.

    Args:
      application_identifier (ApplicationIdentifier): application identifier.
    """
    self.WriteValue(
        application_identifier.guid, application_identifier.description)


def Main():
  """Entry point of console script to extract Windows AppIDs.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the Windows application identifiers (AppID) from the Windows '
      'Registry.'))

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
    return 1

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
    return 1

  collector_object = application_identifiers.ApplicationIdentifiersCollector(
      debug=options.debug)

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return 1

  try:
    has_results = False
    for application_identifier in collector_object.Collect(scanner.registry):
      output_writer_object.WriteApplicationIdentifier(application_identifier)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No Windows application identifiers (AppID) found.')

  return 0


if __name__ == '__main__':
  sys.exit(Main())
