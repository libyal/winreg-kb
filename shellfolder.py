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
import logging
import os
import stat
import sys

import dfvfs
import pyregf
import sqlite3

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.helpers import windows_path_resolver
from dfvfs.resolver import resolver
from dfvfs.vfs import os_file_system
from dfvfs.volume import tsk_volume_system


if dfvfs.__version__ < '20140127':
  raise ImportWarning('shellfolder.py requires dfvfs 20140127 or later.')

if pyregf.get_version() < '20130716':
  raise ImportWarning('shellfolder.py requires pyregf 20130716 or later.')


class CollectorError(Exception):
  """Class that defines collector errors."""


class Collector(object):
  """Class that defines a collector."""

  _WINDOWS_DIRECTORIES = frozenset([
      u'C:\\Windows',
      u'C:\\WINNT',
      u'C:\\WTSRV',
      u'C:\\WINNT35',
  ])

  REGISTRY_FILENAME_SOFTWARE = u'C:\\Windows\\System32\\config\\SOFTWARE'

  def __init__(self):
    """Initializes the collector object."""
    super(Collector, self).__init__()
    self._file_system = None
    self._path_resolver = None
    self.system_root = None

  def GetWindowsVolumePathSpec(self, source_path):
    """Determines the file system path specification of the Windows volume.

    Args:
      source_path: the source path.

    Returns:
      True if successful or False otherwise.

    Raises:
      CollectorError: if the source path does not exists, or if the source path
                      is not a file or directory, or if the format of or within
                      the source file is not supported.
    """
    if not os.path.exists(source_path):
      raise CollectorError(u'No such source: {0:s}.'.format(source_path))

    stat_info = os.stat(source_path)

    if (not stat.S_ISDIR(stat_info.st_mode) and
        not stat.S_ISREG(stat_info.st_mode)):
      raise CollectorError(
          u'Unsupported source: {0:s} not a file or directory.'.format(
              source_path))

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=source_path)

    if stat.S_ISREG(stat_info.st_mode):
      type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise CollectorError((
            u'Unsupported source: {0:s} found more than one storage media '
            u'image types.').format(source_path))

      if len(type_indicators) == 1:
        path_spec = path_spec_factory.Factory.NewPathSpec(
            type_indicators[0], parent=path_spec)

      type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise CollectorError((
            u'Unsupported source: {0:s} found more than one volume system '
            u'types.').format(source_path))

      if len(type_indicators) == 1:
        if type_indicators[0] == definitions.TYPE_INDICATOR_TSK_PARTITION:
          vs_path_spec = path_spec_factory.Factory.NewPathSpec(
              type_indicators[0], location='/', parent=path_spec)

          volume_system = tsk_volume_system.TSKVolumeSystem()
          volume_system.Open(vs_path_spec)

          result = False

          for volume in volume_system.volumes:
            if not hasattr(volume, 'identifier'):
              continue

            volume_location = u'/{0:s}'.format(volume.identifier)
            volume_path_spec = path_spec_factory.Factory.NewPathSpec(
                type_indicators[0], location=volume_location, parent=path_spec)

            fs_path_spec = path_spec_factory.Factory.NewPathSpec(
                definitions.TYPE_INDICATOR_TSK, location=u'/',
                parent=volume_path_spec)
            file_system = resolver.Resolver.OpenFileSystem(fs_path_spec)

            if file_system is None:
              continue

            path_resolver = windows_path_resolver.WindowsPathResolver(
                file_system, volume_path_spec)

            for windows_path in self._WINDOWS_DIRECTORIES:
              windows_path_spec = path_resolver.ResolvePath(windows_path)

              result = windows_path_spec is not None

              if result:
                path_spec = volume_path_spec
                break

            if result:
              break

          if not result:
            return False

        elif type_indicators[0] != definitions.TYPE_INDICATOR_VSHADOW:
          raise CollectorError((
              u'Unsupported source: {0:s} found unsupported volume system '
              u'type: {1:s}.').format(source_path, type_indicators[0]))

      type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
          path_spec)

      if len(type_indicators) == 0:
        return False

      if len(type_indicators) > 1:
        raise CollectorError((
            u'Unsupported source: {0:s} found more than one file system '
            u'types.').format(source_path))

      if type_indicators[0] != definitions.TYPE_INDICATOR_TSK:
        raise CollectorError((
            u'Unsupported source: {0:s} found unsupported file system '
            u'type: {1:s}.').format(source_path, type_indicators[0]))

      fs_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_TSK, location=u'/',
          parent=path_spec)
      self._file_system = resolver.Resolver.OpenFileSystem(fs_path_spec)

    elif stat.S_ISDIR(stat_info.st_mode):
      self._file_system = os_file_system.OSFileSystem()

    self._path_resolver = windows_path_resolver.WindowsPathResolver(
        self._file_system, path_spec)

    return True

  def OpenRegistryFile(self, windows_path):
    """Opens the registry file specificed by the Windows path.

    Args:
      windows_path: the Windows path containing the Registry filename.

    Returns:
      The Registry file (instance of RegistryFile) or None.
    """
    path_spec = self._path_resolver.ResolvePath(windows_path)
    if path_spec is None:
      return None

    file_object = resolver.Resolver.OpenFileObject(path_spec)
    if file_object is None:
      return None

    registry_file = RegistryFile()
    registry_file.Open(file_object)
    return registry_file


class RegistryFile(object):
  """Class that defines a Windows Registry file."""

  _CLASS_IDENTIFIERS_KEY_PATH = 'Classes\\CLSID'

  def __init__(self, ascii_codepage='cp1252'):
    """Initializes the Windows Registry file.

    Args:
      ascii_codepage: optional ASCII string codepage. The default is cp1252
                      (or windows-1252).
    """
    super(RegistryFile, self).__init__()
    self._file_object = None
    self._regf_file = pyregf.file()
    self._regf_file.set_ascii_codepage(ascii_codepage)

  def Open(self, file_object):
    """Opens the Windows Registry file using a file-like object.

    Args:
      file_object: the file-like object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    self._file_object = file_object
    self._regf_file.open_file_object(self._file_object)
    return True

  def Close(self):
    """Closes the Windows Registry file."""
    self._regf_file.close()
    self._file_object.close()
    self._file_object = None

  def GetClassIdentifierKeys(self):
    """Retrieves the class identifier keys.

    Yields:
      A Registry key (instance of pyregf.key).
    """
    class_identifiers_key = self._regf_file.get_key_by_path(
        self._CLASS_IDENTIFIERS_KEY_PATH)

    if class_identifiers_key:
      for class_identifier_key in class_identifiers_key.sub_keys:
        yield class_identifier_key


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
  """Class that defines a sqlite3 writer."""

  _SHELLFOLDER_CREATE_QUERY = (
      'CREATE TABLE shellfolder ( guid TEXT, windows_version TEXT, name TEXT, '
      'localized_string TEXT )')

  _SHELLFOLDER_INSERT_QUERY = (
      'INSERT INTO shellfolder VALUES ( "{0:s}", "{1:s}", "{2:s}", "{3:s}" )')
  
  _SHELLFOLDER_SELECT_QUERY = (
      'SELECT guid FROM shellfolder WHERE guid = "{0:s}" AND '
      'windows_version = "{1:s}"')

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
      self._cursor.execute(self._SHELLFOLDER_CREATE_QUERY)

    return True

  def Close(self):
    """Closes the writer object."""
    self._connection.close()

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to the database.

    Args:
      shell_folder: the shell folder (instance of ShellFolder).
    """
    if not self._create_new_database:
      sql_query = self._SHELLFOLDER_SELECT_QUERY.format(
          shell_folder.guid, self._windows_version)

      self._cursor.execute(sql_query)

      if self._cursor.fetchone():
        have_entry = True
      else:
        have_entry = False
    else:
      have_entry = False

    if not have_entry:
      sql_query = self._SHELLFOLDER_INSERT_QUERY.format(
          shell_folder.guid, self._windows_version, shell_folder.name,
          shell_folder.localized_string)

      self._cursor.execute(sql_query)
      self._connection.commit()
    else:
      logging.info(u'Ignoring duplicate: {0:s}'.format(shell_folder.guid))


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

  def WriteShellFolder(self, shell_folder):
    """Writes the shell folder to stdout.

    Args:
      shell_folder: the shell folder (instance of ShellFolder).
    """
    print '{0:s}\t{1:s}\t{2:s}'.format(
        shell_folder.guid, shell_folder.name, shell_folder.localized_string)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the shell folder class identifiers from the SOFTWARE '
      ' Registry File (REGF).'))

  args_parser.add_argument(
      'source', nargs='?', action='store', metavar='/mnt/c/',
      default=None, help=('path of the volume containing C:\\Windows or the '
                          'filename of a storage media image containing the '
                          'C:\\Windows directory.'))

  args_parser.add_argument(
      '--db', dest='database', action='store', metavar='shellitems.db',
      default=None, help='path of the sqlite3 database to write to.')

  args_parser.add_argument(
      '--winver', dest='windows_version', action='store', metavar='xp',
      default=None, help=('string that identifies the Windows version '
                          'in the database.'))

  options = args_parser.parse_args()

  if not options.source:
    print u'Source value is missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  if options.database and not options.windows_version:
    print 'Windows version missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if not options.database:
    writer = StdoutWriter()
  else:
    writer = Sqlite3Writer(options.database, options.windows_version)

  if not writer.Open():
    print 'Unable to open output writer.'
    print ''
    return False

  collector = Collector()

  if not collector.GetWindowsVolumePathSpec(options.source):
    print (
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source)
    print ''
    return False

  # Determine the shell folder identifiers.
  registry_file = collector.OpenRegistryFile(
      collector.REGISTRY_FILENAME_SOFTWARE)

  found_class_identifiers_key = False
  found_shell_folder_identifier_key = False

  for class_identifier_key in registry_file.GetClassIdentifierKeys():
    found_class_identifiers_key = True
    guid = class_identifier_key.name.lower()

    shell_folder_key = class_identifier_key.get_sub_key_by_name('ShellFolder')
    if shell_folder_key:
      found_shell_folder_identifier_key = True

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

      shell_folder = ShellFolder(guid, name, localized_string)
      writer.WriteShellFolder(shell_folder)

  if not found_class_identifiers_key:
    print 'No class identifiers key found.'
  elif not found_shell_folder_identifier_key:
    print 'No shell folder identifier key found.'

  registry_file.Close()

  writer.Close()

  return True

if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
