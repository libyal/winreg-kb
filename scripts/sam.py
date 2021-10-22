#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Security Account Manager (SAM) information."""

import argparse
import logging
import sys

from dfvfs.helpers import command_line as dfvfs_command_line
from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import collector
from winregrc import output_writers
from winregrc import sam


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Security Account Manager information from a SAM Registry '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SAM Registry file.'))

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
  collector_object = sam.SecurityAccountManagerCollector(
      debug=options.debug, output_writer=output_writer)

  result = collector_object.Collect(registry_collector.registry)
  if not result:
    output_writer.WriteText('No Security Account Manager key found.')
    output_writer.WriteText('')

  else:
    for user_account in collector_object.user_accounts:
      output_writer.WriteValue('Username', user_account.username)
      output_writer.WriteValue('Relative identifier (RID)', user_account.rid)
      output_writer.WriteValue(
          'Primary group identifier', user_account.primary_gid)

      if user_account.full_name:
        output_writer.WriteValue('Full name', user_account.full_name)

      if user_account.comment:
        output_writer.WriteValue('Comment', user_account.comment)

      if user_account.user_comment:
        output_writer.WriteValue('User comment', user_account.user_comment)

      output_writer.WriteFiletimeValue(
          'Last log-in time', user_account.last_login_time)

      output_writer.WriteFiletimeValue(
          'Last password set time', user_account.last_password_set_time)

      output_writer.WriteFiletimeValue(
          'Account expiration time', user_account.account_expiration_time)

      output_writer.WriteFiletimeValue(
          'Last password failure time', user_account.last_password_failure_time)

      output_writer.WriteValue(
          'Number of log-ons', user_account.number_of_logons)
      output_writer.WriteValue(
          'Number of password failures',
          user_account.number_of_password_failures)

      if user_account.codepage:
        output_writer.WriteValue('Codepage', user_account.codepage)

      output_writer.WriteText('')

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
