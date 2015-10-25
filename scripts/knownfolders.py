#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import logging
import sys

from winreg_kb import knownfolders


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Close(self):
    """Closes the output writer object."""
    return

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def WriteKnownFolder(self, known_folder):
    """Writes a known folder to the output.

    Args:
      known_folder: a known folder (instance KnownFolder).
    """
    print(u'{0:s}\t{1:s}\t{2:s}'.format(
        known_folder.guid, known_folder.name, known_folder.localized_name))


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts the known folders from a SOFTWARE Registry File (REGF).'))

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

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = knownfolders.KnownFoldersCollector()

  if not collector_object.GetWindowsVolumePathSpec(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.Collect(output_writer)
  output_writer.Close()

  if not collector_object.found_folder_descriptions_key:
    print(u'No folder descriptions key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
