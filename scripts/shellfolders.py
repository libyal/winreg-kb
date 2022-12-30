#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract shell folder class identifiers."""

import argparse
import logging
import sys

from acstore import sqlite_store

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import shellfolders
from winregrc import volume_scanner


class Sqlite3DatabaseFileWriter(object):
  """SQLite3 database file output writer."""

  def __init__(self, path, windows_version):
    """Initializes a SQLite3 database output writer.

    Args:
      path (str): path of the SQLite3 database file.
      windows_version (str): the Windows version.
    """
    super(Sqlite3DatabaseFileWriter, self).__init__()
    self._path = path
    self._windows_version = windows_version
    self._store = sqlite_store.SQLiteAttributeContainerStore()

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    self._store.Open(path=self._path, read_only=False)

    return True

  def Close(self):
    """Closes the output writer object."""
    self._store.Close()

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to the database.

    Args:
      shell_folder (WindowsShellFolder): the shell folder.
    """
    containers = list(self._store.GetAttributeContainers(
        shell_folder.CONTAINER_TYPE,
        filter_expression=f'identifier == "{shell_folder.identifier}"'))

    if containers:
      # TODO: print duplicates.
      logging.info(f'Ignoring duplicate: {shell_folder.identifier:s}')
    else:
      self._store.AddAttributeContainer(shell_folder)


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to stdout.

    Args:
      shell_folder (WindowsShellFolder): the shell folder.
    """
    print((f'{shell_folder.identifier:s}\t{shell_folder.name:s}\t'
           f'{shell_folder.localized_string:s}'))


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the shell folder class identifiers from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '--db', dest='database', action='store', metavar='shellitems.db',
      default=None, help=(
          'path of the attribute container database to write to.'))

  argument_parser.add_argument(
      '-w', '--windows_version', '--windows-version',
      dest='windows_version', action='store', metavar='Windows XP',
      default=None, help='string that identifies the Windows version.')

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
    return False

  if options.database and not options.windows_version:
    print('Windows version missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

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
    return False

  # TODO: map collector to available Registry keys.
  collector_object = shellfolders.ShellFoldersCollector(
      debug=options.debug)

  if options.database:
    output_writer_object = Sqlite3DatabaseFileWriter(
        options.database, options.windows_version)
  else:
    output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    has_results = False
    for shell_folder in collector_object.Collect(scanner.registry):
      output_writer_object.WriteShellFolder(shell_folder)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No shell folder identifiers found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
