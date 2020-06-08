#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract shell folder class identifiers."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import os
import sqlite3
import sys

from dfvfs.helpers import command_line as dfvfs_command_line

from winregrc import collector
from winregrc import output_writers
from winregrc import shellfolders


class Sqlite3Writer(object):
  """SQLite3 output writer."""

  _SHELL_FOLDER_CREATE_QUERY = (
      'CREATE TABLE shell_folder ( guid TEXT, name TEXT )')

  _SHELL_FOLDER_INSERT_QUERY = (
      'INSERT INTO shell_folder VALUES ( "{0:s}", "{1:s}" )')

  _SHELL_FOLDER_SELECT_QUERY = (
      'SELECT name FROM shell_folder WHERE guid = "{0:s}"')

  _LOCALIZED_NAME_CREATE_QUERY = (
      'CREATE TABLE localized_name ( guid TEXT, reference TEXT )')

  _LOCALIZED_NAME_INSERT_QUERY = (
      'INSERT INTO localized_name VALUES ( "{0:s}", "{1:s}" )')

  _LOCALIZED_NAME_SELECT_QUERY = (
      'SELECT reference FROM localized_name WHERE guid = "{0:s}"')

  _VERSION_CREATE_QUERY = (
      'CREATE TABLE version ( guid TEXT, windows_version TEXT )')

  _VERSION_INSERT_QUERY = (
      'INSERT INTO version VALUES ( "{0:s}", "{1:s}" )')

  _VERSION_SELECT_QUERY = (
      'SELECT windows_version FROM version WHERE guid = "{0:s}"')

  def __init__(self, database_file, windows_version):
    """Initializes the output writer object.

    Args:
      database_file (str): the name of the database file.
      windows_version (str): the Windows version.
    """
    super(Sqlite3Writer, self).__init__()
    self._connection = None
    self._create_new_database = False
    self._cursor = None
    self._database_file = database_file
    self._windows_version = windows_version

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    if os.path.exists(self._database_file):
      self._create_new_database = False
    else:
      self._create_new_database = True

    self._connection = sqlite3.connect(self._database_file)
    if not self._connection:
      return False

    self._cursor = self._connection.cursor()
    if not self._cursor:
      return False

    if self._create_new_database:
      self._cursor.execute(self._SHELL_FOLDER_CREATE_QUERY)
      self._cursor.execute(self._LOCALIZED_NAME_CREATE_QUERY)
      self._cursor.execute(self._VERSION_CREATE_QUERY)

    return True

  def Close(self):
    """Closes the output writer object."""
    self._connection.close()

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to the database.

    Args:
      shell_folder (ShellFolder): the shell folder.
    """
    if self._create_new_database:
      have_entry = False
    else:
      sql_query = self._SHELL_FOLDER_SELECT_QUERY.format(shell_folder.guid)

      self._cursor.execute(sql_query)

      have_entry = bool(self._cursor.fetchone())

    if not have_entry:
      sql_query = self._SHELL_FOLDER_INSERT_QUERY.format(
          shell_folder.guid, shell_folder.name)

      sql_query = self._LOCALIZED_NAME_INSERT_QUERY.format(
          shell_folder.guid, shell_folder.localized_string)

      sql_query = self._VERSION_INSERT_QUERY.format(
          shell_folder.guid, self._windows_version)

      self._cursor.execute(sql_query)
      self._connection.commit()
    else:
      # TODO: print duplicates.
      logging.info('Ignoring duplicate: {0:s}'.format(shell_folder.guid))


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to stdout.

    Args:
      shell_folder (ShellFolder): the shell folder.
    """
    print('{0:s}\t{1:s}\t{2:s}'.format(
        shell_folder.guid, shell_folder.name, shell_folder.localized_string))


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the shell folder class identifiers from a SOFTWARE Registry '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '--db', dest='database', action='store', metavar='shellitems.db',
      default=None, help='path of the sqlite3 database to write to.')

  argument_parser.add_argument(
      '--winver', dest='windows_version', action='store', metavar='xp',
      default=None, help=(
          'string that identifies the Windows version in the database.'))

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

  if not options.database:
    output_writer_object = StdoutWriter()
  else:
    output_writer_object = Sqlite3Writer(
        options.database, options.windows_version)

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
  collector_object = shellfolders.ShellFoldersCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No shell folder identifier keys found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
