#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the shell folder class identifiers
# from the SOFTWARE Registry file (REGF)
#
# Copyright (c) 2013, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import sys

import pyregf
import sqlite3


class Sqlite3Writer(object):
  """Class that defines a sqlite3 writer."""

  _CREATE_QUERY = (
      'CREATE TABLE shellfolder ( guid TEXT, windows_version TEXT, name TEXT, '
      'localized_string TEXT )')

  _SELECT_QUERY = (
      'SELECT guid FROM shellfolder WHERE guid = "{0:s}" AND '
      'windows_version = "{1:s}"')

  _INSERT_QUERY = (
      'INSERT INTO shellfolder VALUES ( "{0:s}", "{1:s}", "{2:s}", "{3:s}" )')
  
  def __init__(self, database_file, windows_version):
    """Initializes the writer object.

    Args:
      database_file: the name of the database file.
      windows_version: the Windows version.
    """
    super(Sqlite3Writer, self).__init__()
    self._database_file = database_file
    self._windows_version = windows_version

  def Open(self):
    """Opens the writer object.

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
      self._cursor.execute(self._CREATE_QUERY)

    return True

  def Close(self):
    """Closes the writer object."""
    self._connection.close()

  def WriteShellFolderClassIdentifier(self, guid, name, localized_string):
    """Writes the shell folder class identifier to the database.

    Args:
      guid: the GUID.
      name: the name.
      localized_string: localized string of the name.
    """
    if not self._create_new_database:
      sql_query = self._SELECT_QUERY.format(guid, self._windows_version)

      self._cursor.execute(sql_query)

      if self._cursor.fetchone():
        have_entry = True
      else:
        have_entry = False
    else:
      have_entry = False

    if not have_entry:
      sql_query = self._INSERT_QUERY.format(
          guid, self._windows_version, name, localized_string)

      self._cursor.execute(sql_query)
      self._connection.commit()
    else:
      print 'Ignoring duplicate: {0:s}'.format(guid)


class StdoutWriter(object):
  """Class that defines a stdout writer."""

  def Open(self):
    """Opens the writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the writer object."""
    pass

  def WriteShellFolderClassIdentifier(self, guid, name, localized_string):
    """Writes the shell folder class identifier to stdout.

    Args:
      guid: the GUID.
      name: the name.
      localized_string: localized string of the name.
    """
    print '{0:s}\t{1:s}\t{2:s}'.format(guid, name, localized_string)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the shell folder class identifiers from a SOFTWARE '
      ' Registry File (REGF).'))

  args_parser.add_argument(
      'registry_file', nargs='?', action='store', metavar='SOFTWARE',
      default=None, help='path of the SOFTWARE Registry file.')

  args_parser.add_argument(
      '--db', dest='database', action='store', metavar='shellitems.db',
      default=None, help='path of the sqlite3 database to write to.')

  args_parser.add_argument(
      '--winver', dest='windows_version', action='store', metavar='xp',
      default=None, help=('string that identifies the Windows version '
                          'in the database.'))

  options = args_parser.parse_args()

  if not options.registry_file:
    print 'Registry file missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  if options.database and not options.windows_version:
    print 'Windows version missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  if not options.database:
    writer = StdoutWriter()
  else:
    writer = Sqlite3Writer(options.database, options.windows_version)

  if not writer.Open():
    print 'Unable to open output writer.'
    print ''
    return False

  regf_file = pyregf.file()
  regf_file.open(options.registry_file)

  class_identifiers_key_path = 'Classes\\CLSID'

  class_identifiers_key = regf_file.get_key_by_path(class_identifiers_key_path)

  if class_identifiers_key:
    for class_identifier_key in class_identifiers_key.sub_keys:
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.get_sub_key_by_name('ShellFolder')
      if shell_folder_key:
        value = class_identifier_key.get_value_by_name('')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode('utf-16-le')[:-1]
        else:
          name = ''

        value = class_identifier_key.get_value_by_name('LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode('utf-16-le')[:-1]
        else:
          localized_string = ''

        writer.riteShellFolderClassIdentifier name, localized_string)
  else:
    print 'No class identifiers key found.'

  regf_file.close()

  writer.Close()

  return True

if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
