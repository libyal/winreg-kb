#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract information from the Windows Registry."""

from __future__ import print_function
import argparse
import logging
import sys

from winregrc import collector
from winregrc import knownfolders
from winregrc import output_writer


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder (KnownFolder): known folder.
    """
    print(u'{0:s}\t{1:s}\t{2:s}'.format(
        known_folder.guid, known_folder.name, known_folder.localized_name))


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts information for the Windows Registry.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a Windows Registry file.'))

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
  collector_object = knownfolders.KnownFoldersCollector(debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print(u'No Folder Descriptions key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
