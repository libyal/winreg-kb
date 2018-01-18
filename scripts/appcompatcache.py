#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract Application Compatibility Cache information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfdatetime import filetime as dfdatetime_filetime

from winregrc import appcompatcache
from winregrc import collector
from winregrc import output_writer


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteCachedEntry(self, cached_entry):
    """Writes the Application Compatibility Cache cached entry to stdout.

    Args:
      cached_entry (AppCompatCacheCachedEntry): Application Compatibility
          Cache cached entry.
    """
    filetime = dfdatetime_filetime.Filetime(
        timestamp=cached_entry.last_modification_time)
    date_time_string = filetime.CopyToDateTimeString()

    print('Last modification time\t: {0:s}'.format(date_time_string))
    print('Path\t\t\t: {0:s}'.format(cached_entry.path))


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
          'a storage media image containing the C:\\Windows directory,'
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

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = appcompatcache.AppCompatCacheCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object,
      all_control_sets=options.all_control_sets)
  if not result:
    print('No Application Compatibility Cache key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
