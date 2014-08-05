#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the shell folder class identifiers
# from the SOFTWARE Registry file (REGF)
#
# Copyright (c) 2013-2014, Joachim Metz <joachim.metz@gmail.com>
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
import sys

import dfvfs
import pyregf
import sqlite3

from dfvfs.lib import definitions
from dfvfs.helpers import source_scanner
from dfvfs.helpers import windows_path_resolver
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system


if dfvfs.__version__ < '20140727':
  raise ImportWarning('shellfolder.py requires dfvfs 20140727 or later.')

if pyregf.get_version() < '20130716':
  raise ImportWarning('shellfolder.py requires pyregf 20130716 or later.')


class CollectorError(Exception):
  """Class that defines collector errors."""


class WindowsVolumeCollector(object):
  """Class that defines a Windows volume collector."""

  _WINDOWS_DIRECTORIES = frozenset([
      u'C:\\Windows',
      u'C:\\WINNT',
      u'C:\\WTSRV',
      u'C:\\WINNT35',
  ])

  def __init__(self):
    """Initializes the Windows volume collector object."""
    super(WindowsVolumeCollector, self).__init__()
    self._file_system = None
    self._path_resolver = None
    self._scanner = source_scanner.SourceScanner()
    self._windows_directory = None

  def _ScanFileSystem(self, path_resolver):
    """Scans a file system for the Windows volume.

    Args:
      path_resolver: the path resolver (instance of dfvfs.WindowsPathResolver).

    Returns:
      True if the Windows directory was found, false otherwise.

    """
    result = False

    for windows_path in self._WINDOWS_DIRECTORIES:
      windows_path_spec = path_resolver.ResolvePath(windows_path)

      result = windows_path_spec is not None
      if result:
        self._windows_directory = windows_path
        break

    return result

  def _ScanTSKPartionVolumeSystemPathSpec(self, scan_context):
    """Scans a path specification for the Windows volume.

    Args:
      scan_context: the scan context (instance of dfvfs.ScanContext).

    Returns:
      The volume scan node (instance of dfvfs.ScanNode) of the volume that
      contains the Windows directory or None.

    Raises:
      CollectorError: if the scan context is invalid.
    """
    if (not scan_context or not scan_context.last_scan_node or
        not scan_context.last_scan_node.path_spec):
      raise CollectorError(u'Invalid scan context.')

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(scan_context.last_scan_node.path_spec)

    volume_identifiers = self._scanner.GetVolumeIdentifiers(volume_system)
    if not volume_identifiers:
      return False

    volume_scan_node = None
    result = False

    for volume_identifier in volume_identifiers:
      volume_location = u'/{0:s}'.format(volume_identifier)
      volume_scan_node = scan_context.last_scan_node.GetSubNodeByLocation(
          volume_location)
      volume_path_spec = getattr(volume_scan_node, 'path_spec', None)

      file_system_scan_node = volume_scan_node.GetSubNodeByLocation(u'/')
      file_system_path_spec = getattr(file_system_scan_node, 'path_spec', None)
      file_system = resolver.Resolver.OpenFileSystem(file_system_path_spec)

      if file_system is None:
        continue

      path_resolver = windows_path_resolver.WindowsPathResolver(
          file_system, volume_path_spec)

      result = self._ScanFileSystem(path_resolver)
      if result:
        break

    if result:
      return volume_scan_node

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

    scan_context = source_scanner.SourceScannerContext()
    scan_path_spec = None

    scan_context.OpenSourcePath(source_path)

    while True:
      scan_context = self._scanner.Scan(
          scan_context, scan_path_spec=scan_path_spec)

      # The source is a directory or file.
      if scan_context.source_type in [
          scan_context.SOURCE_TYPE_DIRECTORY, scan_context.SOURCE_TYPE_FILE]:
        break

      if not scan_context.last_scan_node:
        raise CollectorError(
            u'No supported file system found in source: {0:s}.'.format(
                source_path))

      # The source scanner found a file system.
      if scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_TSK]:
        break

      # The source scanner found a BitLocker encrypted volume and we need
      # a credential to unlock the volume.
      if scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_BDE]:
        # TODO: ask for password.
        raise CollectorError(
            u'BitLocker encrypted volume not yet supported.')

      # The source scanner found a partition table and we need to determine
      # which partition contains the Windows directory.
      elif scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_TSK_PARTITION]:
        scan_node = self._ScanTSKPartionVolumeSystemPathSpec(scan_context)
        if not scan_node:
          return False
        scan_context.last_scan_node = scan_node

      # The source scanner found Volume Shadow Snapshot which is ignored.
      elif scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_VSHADOW]:
        scan_node = scan_context.last_scan_node.GetSubNodeByLocation(u'/')
        scan_context.last_scan_node = scan_node
        break

      else:
        raise CollectorError(
            u'Unsupported volume system found in source: {0:s}.'.format(
                source_path))

    # TODO: add single file support.
    if scan_context.source_type == scan_context.SOURCE_TYPE_FILE:
      raise CollectorError(
          u'Unsupported source: {0:s}.'.format(source_path))

    if scan_context.source_type != scan_context.SOURCE_TYPE_DIRECTORY:
      if not scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_TSK]:
        raise CollectorError(
            u'Unsupported source: {0:s} found unsupported file system.'.format(
                source_path))

    file_system_path_spec = getattr(
        scan_context.last_scan_node, 'path_spec', None)
    self._file_system = resolver.Resolver.OpenFileSystem(
        file_system_path_spec)

    if file_system_path_spec.type_indicator == definitions.TYPE_INDICATOR_OS:
      mount_point = file_system_path_spec
    else:
      mount_point = file_system_path_spec.parent

    self._path_resolver = windows_path_resolver.WindowsPathResolver(
        self._file_system, mount_point)

    if scan_context.source_type == scan_context.SOURCE_TYPE_DIRECTORY:
      if not self._ScanFileSystem(self._path_resolver):
        return False

    self._path_resolver.SetEnvironmentVariable(
        'WinDir', self._windows_directory)

    return True

  def OpenFile(self, windows_path):
    """Opens the file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the file.

    Returns:
      The file-like object (instance of dfvfs.FileIO) or None if
      the file does not exist.
    """
    path_spec = self._path_resolver.ResolvePath(windows_path)
    if path_spec is None:
      return None

    return resolver.Resolver.OpenFileObject(path_spec)


class ShellFolderIdentifierCollector(WindowsVolumeCollector):
  """Class that defines a Shell Folder identifier collector."""

  _REGISTRY_FILENAME_SOFTWARE = u'%WinDir%\\System32\\config\\SOFTWARE'

  def __init__(self):
    """Initializes the Shell Folder identifier collector object."""
    super(ShellFolderIdentifierCollector, self).__init__()
    self.found_class_identifiers_key = False
    self.found_shell_folder_identifier_key = False

  def _OpenRegistryFile(self, windows_path):
    """Opens the Registry file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the Registry file.

    Returns:
      The Registry file (instance of RegistryFile) or None.
    """
    file_object = self.OpenFile(windows_path)
    if file_object is None:
      return None

    registry_file = RegistryFile()
    registry_file.Open(file_object)
    return registry_file

  def CollectShellFolderIdentifiers(self, output_writer):
    """Collects the Shell Folder identifiers from the SOFTWARE Registry file.

    Args:
      output_writer: the output writer object.
    """
    registry_file = self._OpenRegistryFile(self._REGISTRY_FILENAME_SOFTWARE)

    for class_identifier_key in registry_file.GetClassIdentifierKeys():
      self.found_class_identifiers_key = True
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.get_sub_key_by_name('ShellFolder')
      if shell_folder_key:
        self.found_shell_folder_identifier_key = True

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
        output_writer.WriteShellFolder(shell_folder)

    registry_file.Close()


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
  """Class that defines a sqlite3 output writer."""

  _SHELLFOLDER_CREATE_QUERY = (
      'CREATE TABLE shellfolder ( guid TEXT, windows_version TEXT, name TEXT, '
      'localized_string TEXT )')

  _SHELLFOLDER_INSERT_QUERY = (
      'INSERT INTO shellfolder VALUES ( "{0:s}", "{1:s}", "{2:s}", "{3:s}" )')

  _SHELLFOLDER_SELECT_QUERY = (
      'SELECT guid FROM shellfolder WHERE guid = "{0:s}" AND '
      'windows_version = "{1:s}"')

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
      self._cursor.execute(self._SHELLFOLDER_CREATE_QUERY)

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
    print u'{0:s}\t{1:s}\t{2:s}'.format(
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
    print u'Windows version missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  if not options.database:
    output_writer = StdoutWriter()
  else:
    output_writer = Sqlite3Writer(options.database, options.windows_version)

  if not output_writer.Open():
    print u'Unable to open output writer.'
    print u''
    return False

  collector = ShellFolderIdentifierCollector()

  if not collector.GetWindowsVolumePathSpec(options.source):
    print (
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source)
    print ''
    return False

  collector.CollectShellFolderIdentifiers(output_writer)
  output_writer.Close()

  if not collector.found_class_identifiers_key:
    print u'No class identifiers key found.'
  elif not collector.found_shell_folder_identifier_key:
    print u'No shell folder identifier key found.'

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
