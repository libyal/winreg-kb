#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract services information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfvfs.helpers import command_line as dfvfs_command_line

from winregrc import collector
from winregrc import output_writers
from winregrc import services


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def __init__(self, use_tsv=False):
    """Initializes a stdout output writer.

    Args:
      use_tsv (bool): True if the output should in tab separated values.
    """
    super(StdoutWriter, self).__init__()
    self._printed_header = False
    self._use_tsv = use_tsv

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service (WindowsService): Windows service.
    """
    service_type_description = ''
    if service.service_type:
      service_type_description = service.GetServiceTypeDescription()

    start_value_description = ''
    if service.start_value is not None:
      start_value_description = service.GetStartValueDescription()

    if self._use_tsv:
      if not self._printed_header:
        print('Service\tType\tDisplay name\tDescription\tExecutable\tStart')
        self._printed_header = True

      service_display_name = service.display_name or ''
      service_description = service.description or ''
      service_image_path = service.image_path or ''

      print('{0:s}\t{1:s}\t{2:s}\t{3:s}\t{4:s}\t{5:s}'.format(
          service.name, service_type_description, service_display_name,
          service_description, service_image_path, start_value_description))

    else:
      print('{0:s}'.format(service.name))

      if service.service_type:
        print('\tType\t\t\t: {0:s}'.format(service_type_description))

      if service.display_name:
        print('\tDisplay name\t\t: {0:s}'.format(service.display_name))

      if service.description:
        print('\tDescription\t\t: {0:s}'.format(service.description))

      if service.image_path:
        print('\tExecutable\t\t: {0:s}'.format(service.image_path))

      if service.object_name:
        print('\t{0:s}\t\t: {1:s}'.format(
            service.GetObjectNameDescription(), service.object_name))

      if service.start_value is not None:
        print('\tStart\t\t\t: {0:s}'.format(start_value_description))

      print('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the services information from a SYSTEM Registry file.'))

  argument_parser.add_argument(
      '--all', dest='all_control_sets', action='store_true', default=False,
      help=(
          'Process all control sets instead of only the current control set.'))

  argument_parser.add_argument(
      '--diff', dest='diff_control_sets', action='store_true', default=False,
      help='Only list differences between control sets.')

  argument_parser.add_argument(
      '--tsv', dest='use_tsv', action='store_true', default=False,
      help='Use tab separated value (TSV) output.')

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

  output_writer_object = StdoutWriter(use_tsv=options.use_tsv)

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
  collector_object = services.WindowsServicesCollector(
      debug=options.debug)

  if options.diff_control_sets:
    result = collector_object.Compare(
        registry_collector.registry, output_writer_object)
  else:
    result = collector_object.Collect(
        registry_collector.registry, output_writer_object,
        all_control_sets=options.all_control_sets)

  if not result:
    print('No Services key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
