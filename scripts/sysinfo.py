#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract system information."""

from __future__ import print_function
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
    self.WriteValue(u'Product name', system_information.product_name)
    self.WriteValue(
        u'Product identifier', system_information.product_identifier)

    self.WriteValue(u'Current version', system_information.current_version)
    self.WriteValue(u'Current type', system_information.current_type)
    self.WriteValue(
        u'Current build number', system_information.current_build_number)
    self.WriteValue(u'CSD version', system_information.csd_version)

    self.WriteValue(
        u'Registered organization', system_information.registered_organization)
    self.WriteValue(u'Registered owner', system_information.registered_owner)

    # TODO: write date and time as human readable string.
    self.WriteValue(u'Installation date', system_information.installation_date)

    self.WriteValue(u'Path name', system_information.path_name)
    self.WriteValue(u'%SystemRoot%', system_information.system_root)

    self.WriteText(u'')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts the system information from a SOFTWARE Registry file.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print(u'Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print(u'')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = sysinfo.SystemInfoCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print(u'No Current Version key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
