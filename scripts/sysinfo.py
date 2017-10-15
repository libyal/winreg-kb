#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract system information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from winregrc import collector
from winregrc import output_writer
from winregrc import sysinfo


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteSystemInformation(self, system_information):
    """Writes system information to stdout.

    Args:
      system_information (SystemInformation): system information to write.
    """
    self.WriteValue('Product name', system_information.product_name)
    self.WriteValue(
        'Product identifier', system_information.product_identifier)

    self.WriteValue('Current version', system_information.current_version)
    self.WriteValue('Current type', system_information.current_type)
    self.WriteValue(
        'Current build number', system_information.current_build_number)
    self.WriteValue('CSD version', system_information.csd_version)

    self.WriteValue(
        'Registered organization', system_information.registered_organization)
    self.WriteValue('Registered owner', system_information.registered_owner)

    # TODO: write date and time as human readable string.
    self.WriteValue('Installation date', system_information.installation_date)

    self.WriteValue('Path name', system_information.path_name)
    self.WriteValue('%SystemRoot%', system_information.system_root)

    self.WriteText('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the system information from a SOFTWARE Registry file.'))

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
  collector_object = sysinfo.SystemInfoCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No Current Version key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
