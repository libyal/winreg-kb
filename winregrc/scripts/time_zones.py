#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract tize zone information from the Windows Registry."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import time_zones
from winregrc import output_writers
from winregrc import volume_scanner


class CSVFileWriter(output_writers.OutputWriter):
  """CSV file output writer."""

  # pylint: disable=abstract-method

  def __init__(self, path):
    """Initializes a CSV file output writer.

    Args:
      path (str): path of the CSV file to write to.
    """
    super(CSVFileWriter, self).__init__()
    self._file_object = None
    self._path = path

  def Close(self):
    """Closes the output writer."""
    self._file_object.close()
    self._file_object = None

  def Open(self):
    """Opens the output writer.

    Returns:
      bool: True if successful or False if not.
    """
    # self._file_object = open(self._path, 'wt', encoding='utf-8')
    self._file_object = open(self._path, 'at', encoding='utf-8')  # pylint: disable=consider-using-with
    return 0

  def WriteTimeZone(self, time_zone):
    """Writes a time zone to the output.

    Args:
      time_zone (TimeZone): time zone.
    """
    hours_from_utc, minutes_from_utc = divmod(time_zone.offset, 60)

    if hours_from_utc < 0:
      hours_from_utc *= -1
      sign = '-'
    else:
      sign = '+'

    self._file_object.write((
        f'{time_zone.name:s},{sign:s}{hours_from_utc:02d}:'
        f'{minutes_from_utc:02d}\n'))

  def WriteText(self, text):
    """Writes text.

    Args:
      text (str): text to write.
    """
    return


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteTimeZone(self, time_zone):
    """Writes a time zone to the output.

    Args:
      time_zone (TimeZone): time zone.
    """
    hours_from_utc, minutes_from_utc = divmod(time_zone.offset, 60)

    if hours_from_utc < 0:
      hours_from_utc *= -1
      sign = '-'
    else:
      sign = '+'

    self.WriteText((
        f'{time_zone.name:s}\t{sign:s}{hours_from_utc:02d}:'
        f'{minutes_from_utc:02d}\n'))


def Main():
  """Entry point of console script to extract tize zone information.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts time zone information for the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '--csv', dest='csv_file', action='store', metavar='time_zones.csv',
      default=None, help='path of the CSV file to write to.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return 1

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  if options.csv_file:
    output_writer_object = CSVFileWriter(options.csv_file)
  else:
    output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return 1

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

  # TODO: map collector to available Registry keys.
  collector_object = time_zones.TimeZonesCollector(debug=options.debug)

  result = collector_object.Collect(scanner.registry, output_writer_object)
  if not result:
    print('No "Time Zones" key found.')

  output_writer_object.Close()

  return 0


if __name__ == '__main__':
  sys.exit(Main())
