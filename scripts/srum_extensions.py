#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract System Resource Usage Monitor (SRUM) extensions."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import srum_extensions
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteSRUMExtension(self, srum_extension):
    """Writes a SRUM extension to the output.

    Args:
      srum_extension (SRUMExtension): SRUM extension.
    """
    text = '{0:s}\t{1:s}\n'.format(srum_extension.guid, srum_extension.dll_name)
    self.WriteText(text)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the User Assist information from a NTUSER.DAT Registry file.'))

  argument_parser.add_argument(
      '--codepage', dest='codepage', action='store', metavar='CODEPAGE',
      default='cp1252', help='the codepage of the extended ASCII strings.')

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a NTUSER.DAT Registry file.'))

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

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  if not scanner.ScanForWindowsVolume(
      options.source, options=volume_scanner_options):
    print(('Unable to retrieve the volume with the Windows directory from: '
           '{0:s}.').format(options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = srum_extensions.SRUMExtensionsCollector(
      debug=options.debug)

  result = collector_object.Collect(scanner.registry, output_writer_object)
  if not result:
    print('No SRUM extensions key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
