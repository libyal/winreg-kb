#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract user profiles."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import profiles
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteUserProfile(self, user_profile):
    """Writes an user profile to the output.

    Args:
      user_profile (UserProfile): user profile.
    """
    self.WriteText((
        f'{user_profile.security_identifier:s}: '
        f'{user_profile.home_directory:s}\n'))


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
  collector_object = profiles.UserProfilesCollector(
      debug=options.debug)

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    has_results = False
    for user_profile in collector_object.Collect(scanner.registry):
      output_writer_object.WriteUserProfile(user_profile)
      has_results = True

    if has_results:
      output_writer_object.WriteText('\n')

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No user profiles found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
