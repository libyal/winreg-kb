#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract user profiles."""

import argparse
import logging
import sys

from dfvfs.helpers import command_line as dfvfs_command_line
from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import collector
from winregrc import output_writers
from winregrc import profiles


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text (str): text to write.
    """
    print(text)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the user profiles from the Windows Registry.'))

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

  mediator = dfvfs_command_line.CLIVolumeScannerMediator()
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

  # TODO: map collector to available Registry keys.
  collector_object = profiles.UserProfilesCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No Profile List key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
