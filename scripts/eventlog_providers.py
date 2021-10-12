#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract EventLog providers from the Windows Registry."""

import argparse
import logging
import sys

from dfvfs.helpers import command_line as dfvfs_command_line

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
    text = '{0:s}\t{1:s}\t{2:s}\t{3:s}\t{4:s}\n'.format(
        eventlog_provider.log_source,
        eventlog_provider.log_type,
        ';'.join(eventlog_provider.category_message_files),
        ';'.join(eventlog_provider.event_message_files),
        ';'.join(eventlog_provider.parameter_message_files))
    self.WriteText(text)


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

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  volume_scanner_mediator = dfvfs_command_line.CLIVolumeScannerMediator()
  registry_collector = collector.WindowsRegistryCollector(
      mediator=volume_scanner_mediator)
  if not registry_collector.ScanForWindowsVolume(options.source):
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
    print('No "EventLog" key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
