#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract Windows Event Log providers from the Windows Registry."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import eventlog_providers
from winregrc import output_writers
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteEventLogProvider(self, eventlog_provider):
    """Writes a Event Log provider to the output.

    Args:
      eventlog_provider (EventLogProvider): Event Log provider.
    """
    if eventlog_provider.name:
      self.WriteText(f'Name\t\t\t\t: {eventlog_provider.name:s}\n')

    if eventlog_provider.identifier:
      self.WriteText(f'Identifier\t\t\t: {eventlog_provider.identifier:s}\n')

    if eventlog_provider.additional_identifier:
      self.WriteText((
          f'Additional identifier\t\t: '
          f'{eventlog_provider.additional_identifier:s}\n'))

    for index, log_type in enumerate(sorted(eventlog_provider.log_types)):
      if index == 0:
        text = f'Log type(s)\t\t\t: {log_type:s}\n'
      else:
        text = f'\t\t\t\t: {log_type:s}\n'
      self.WriteText(text)

    for index, log_source in enumerate(sorted(eventlog_provider.log_sources)):
      if index == 0:
        text = f'Log source(s)\t\t\t: {log_source:s}\n'
      else:
        text = f'\t\t\t\t: {log_source:s}\n'
      self.WriteText(text)

    for index, path in enumerate(sorted((
        eventlog_provider.category_message_files))):
      if index == 0:
        text = f'Category message file(s)\t: {path:s}\n'
      else:
        text = f'\t\t\t\t: {path:s}\n'
      self.WriteText(text)

    for index, path in enumerate(sorted((
        eventlog_provider.event_message_files))):
      if index == 0:
        text = f'Event message file(s)\t\t: {path:s}\n'
      else:
        text = f'\t\t\t\t: {path:s}\n'
      self.WriteText(text)

    for index, path in enumerate(sorted((
        eventlog_provider.parameter_message_files))):
      if index == 0:
        text = f'Parameter message file(s)\t: {path:s}\n'
      else:
        text = f'\t\t\t\t: {path:s}\n'
      self.WriteText(text)

    self.WriteText('\n')


def Main():
  """Entry point of console script to extract Event Log providers.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Windows Event Log providers from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=('path of the volume containing C:\\Windows, the filename of '
            'a storage media image containing the C:\\Windows directory, '
            'or the path of a SOFTWARE or SYSTEM Registry file.'))

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

  collector_object = eventlog_providers.EventLogProvidersCollector(
      debug=options.debug)

  output_writer_object = StdoutWriter()
  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return 1

  try:
    has_results = False
    for eventlog_provider in collector_object.Collect(scanner.registry):
      output_writer_object.WriteEventLogProvider(eventlog_provider)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No Windows Event Log providers found.')

  return 0


if __name__ == '__main__':
  sys.exit(Main())
