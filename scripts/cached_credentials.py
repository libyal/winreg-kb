#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract cached credentials."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfvfs.helpers import command_line as dfvfs_command_line

from winregrc import cached_credentials
from winregrc import collector
from winregrc import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the cached credentials from a SECURITY Registry file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False, help=(
          'enable debug output.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SECURITY and SYSTEM Registry file.'))

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

  volume_scanner_mediator = dfvfs_command_line.CLIVolumeScannerMediator()
  registry_collector = collector.WindowsRegistryCollector(
      mediator=volume_scanner_mediator)
  if not registry_collector.ScanForWindowsVolume(options.source):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  if registry_collector.IsSingleFileRegistry():
    print('Both SECURITY and SYSYEM Registry files are required.')
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = cached_credentials.CachedCredentialsKeyCollector(
      debug=options.debug, output_writer=output_writer)

  result = collector_object.Collect(registry_collector.registry)
  if not result:
    print('No Cache key found.')
  else:
    output_writer.WriteText('\n')

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
