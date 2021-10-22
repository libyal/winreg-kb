#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract UserAssist information."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import collector
from winregrc import output_writers
from winregrc import userassist


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the UserAssist information from a NTUSER.DAT Registry file.'))

  argument_parser.add_argument(
      '--codepage', dest='codepage', action='store', metavar='CODEPAGE',
      default='cp1252', help='the codepage of the extended ASCII strings.')

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a NTUSER.DAT Registry file.'))

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

  # TODO: map collector to available Registry keys.
  collector_object = userassist.UserAssistCollector(
      debug=options.debug, output_writer=output_writer)

  result = collector_object.Collect(registry_collector.registry)
  if not result:
    print('No UserAssist key found.')
  else:
    guid = None
    for user_assist_entry in collector_object.user_assist_entries:
      if user_assist_entry.guid != guid:
        print('GUID\t\t: {0:s}'.format(user_assist_entry.guid))
        guid = user_assist_entry.guid

      print('Name\t\t: {0:s}'.format(user_assist_entry.name))
      print('Original name\t: {0:s}'.format(user_assist_entry.value_name))

  print('')
  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
