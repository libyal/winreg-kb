#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract EventLog providers from the Windows Registry."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import collector
from winregrc import eventlog_providers
from winregrc import output_writers


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteEventLogProvider(self, eventlog_provider):
    """Writes a EventLog provider to the output.

    Args:
      eventlog_provider (EventLogProvider): EventLog provider.
    """
    text = 'Log source\t\t: {0:s}\n'.format(eventlog_provider.log_source)
    self.WriteText(text)

    if eventlog_provider.log_source_alias:
      text = 'Log source alias\t: {0:s}\n'.format(
          eventlog_provider.log_source_alias)
      self.WriteText(text)

    if eventlog_provider.identifier:
      text = 'Identifier\t\t: {0:s}\n'.format(eventlog_provider.identifier)
      self.WriteText(text)

    if eventlog_provider.log_type:
      text = 'Log type\t\t: {0:s}\n'.format(eventlog_provider.log_type)
      self.WriteText(text)

    if eventlog_provider.category_message_files:
      text = 'Category message files\t: {0:s}\n'.format(
          ';'.join(eventlog_provider.category_message_files))
      self.WriteText(text)

    if eventlog_provider.event_message_files:
      text = 'Event message files\t: {0:s}\n'.format(
          ';'.join(eventlog_provider.event_message_files))
      self.WriteText(text)

    if eventlog_provider.parameter_message_files:
      text = 'Parameter message files\t: {0:s}\n'.format(
          ';'.join(eventlog_provider.parameter_message_files))
      self.WriteText(text)

    self.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts EventLog providers from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SOFTWARE or SYSTEM Registry file.'))

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
  collector_object = eventlog_providers.EventLogProvidersCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No "Services\\EventLog" and "WINEVT\\Publishers" keys found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
