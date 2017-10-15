#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract Task Scheduler Task Cache information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from winregrc import collector
from winregrc import output_writer
from winregrc import task_cache


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteCachedTask(self, cached_task):
    """Writes a cached task to stdout.

    Args:
      cached_task (CachedTask): the cached task to write.
    """
    self.WriteValue('Task', cached_task.name)
    self.WriteValue('Identifier', cached_task.identifier)

    # TODO: write date and time as human readable string.
    self.WriteValue('Last registered time', cached_task.last_registered_time)
    self.WriteValue('Launch time', cached_task.launch_time)

    self.WriteText('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Task Scheduler Task Cache information from '
      'a SOFTWARE Registry file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory,'
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

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = task_cache.TaskCacheCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No Task Cache key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
