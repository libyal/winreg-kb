#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

import sqlite3

import collector


# pylint: disable=logging-format-interpolation
# pylint: disable=superfluous-parens

class ShellFolderIdentifierCollector(collector.WindowsRegistryCollector):
  """Class that defines a Shell Folder identifier collector."""

  _CLASS_IDENTIFIERS_KEY_PATH = u'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def __init__(self):
    """Initializes the Shell Folder identifier collector object."""
    super(ShellFolderIdentifierCollector, self).__init__()
    self.found_class_identifiers_key = False
    self.found_shell_folder_identifier_key = False

  def Collect(self, output_writer):
    """Collects the Shell Folder identifiers.

    Args:
      output_writer: the output writer object.
    """
    self.found_class_identifiers_key = False
    class_identifiers_key = self._registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if not class_identifiers_key:
      return

    self.found_class_identifiers_key = True
    for class_identifier_key in class_identifiers_key.sub_keys:
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.get_sub_key_by_name(
          u'ShellFolder')
      if shell_folder_key:
        self.found_shell_folder_identifier_key = True

        value = class_identifier_key.get_value_by_name(u'')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode(u'utf-16-le')[:-1]
        else:
          name = u''

        value = class_identifier_key.get_value_by_name(u'LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode(u'utf-16-le')[:-1]
        else:
          localized_string = u''

        shell_folder = ShellFolder(guid, name, localized_string)
        output_writer.WriteShellFolder(shell_folder)


class ShellFolder(object):
  """Class that defines a shell folder."""

  def __init__(self, guid, name, localized_string):
    """Initializes the shell folder object.

    Args:
      guid: the GUID.
      name: the name.
      localized_string: localized string of the name.
    """
    super(ShellFolder, self).__init__()
    self.guid = guid
    self.name = name
    self.localized_string = localized_string


class Sqlite3Writer(object):
  """Class that defines a sqlite3 output writer."""

  _SHELL_FOLDER_CREATE_QUERY = (
      u'CREATE TABLE shell_folder ( guid TEXT, name TEXT )')

  _SHELL_FOLDER_INSERT_QUERY = (
      u'INSERT INTO shell_folder VALUES ( "{0:s}", "{1:s}" )')

  _SHELL_FOLDER_SELECT_QUERY = (
      u'SELECT name FROM shell_folder WHERE guid = "{0:s}"')

  _LOCALIZED_NAME_CREATE_QUERY = (
      u'CREATE TABLE localized_name ( guid TEXT, reference TEXT )')

  _LOCALIZED_NAME_INSERT_QUERY = (
      u'INSERT INTO localized_name VALUES ( "{0:s}", "{1:s}" )')

  _LOCALIZED_NAME_SELECT_QUERY = (
      u'SELECT reference FROM localized_name WHERE guid = "{0:s}"')

  _VERSION_CREATE_QUERY = (
      u'CREATE TABLE version ( guid TEXT, windows_version TEXT )')

  _VERSION_INSERT_QUERY = (
      u'INSERT INTO version VALUES ( "{0:s}", "{1:s}" )')

  _VERSION_SELECT_QUERY = (
      u'SELECT windows_version FROM version WHERE guid = "{0:s}"')

  def __init__(self, database_file, windows_version):
    """Initializes the output writer object.

    Args:
      database_file: the name of the database file.
      windows_version: the Windows version.
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
      A boolean containing True if successful or False if not.
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
      shell_folder: the shell folder (instance of ShellFolder).
    """
    if not self._create_new_database:
      sql_query = self._SHELL_FOLDER_SELECT_QUERY.format(shell_folder.guid)

      self._cursor.execute(sql_query)

      if self._cursor.fetchone():
        have_entry = True
      else:
        have_entry = False
    else:
      have_entry = False

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
      logging.info(u'Ignoring duplicate: {0:s}'.format(shell_folder.guid))


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to stdout.

    Args:
      shell_folder: the shell folder (instance of ShellFolder).
    """
    print(u'{0:s}\t{1:s}\t{2:s}'.format(
        shell_folder.guid, shell_folder.name, shell_folder.localized_string))


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      u'Extract the shell folder class identifiers from a SOFTWARE Registry '
      u'File (REGF).'))

  args_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SOFTWARE Registry file.'))

  args_parser.add_argument(
      u'--db', dest=u'database', action=u'store', metavar=u'shellitems.db',
      default=None, help=u'path of the sqlite3 database to write to.')

  args_parser.add_argument(
      u'--winver', dest=u'windows_version', action=u'store', metavar=u'xp',
      default=None, help=(
          u'string that identifies the Windows version in the database.'))

  options = args_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    args_parser.print_help()
    print(u'')
    return False

  if options.database and not options.windows_version:
    print(u'Windows version missing.')
    print(u'')
    args_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if not options.database:
    output_writer = StdoutWriter()
  else:
    output_writer = Sqlite3Writer(options.database, options.windows_version)

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = ShellFolderIdentifierCollector()

  if not collector_object.GetWindowsVolumePathSpec(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.Collect(output_writer)
  output_writer.Close()

  if not collector_object.found_class_identifiers_key:
    print(u'No class identifiers key found.')
  elif not collector_object.found_shell_folder_identifier_key:
    print(u'No shell folder identifier key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
