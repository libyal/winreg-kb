#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the drivers and services from the SYSTEM
# Registry file (REGF)
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

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.path import factory as path_spec_factory
from dfvfs.helpers import windows_path_resolver
from dfvfs.resolver import resolver
from dfvfs.vfs import os_file_system
from dfvfs.volume import tsk_volume_system


if dfvfs.__version__ < '20140127':
  raise ImportWarning('services.py requires dfvfs 20140127 or later.')

if pyregf.get_version() < '20130716':
  raise ImportWarning('services.py requires pyregf 20130716 or later.')


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


class WindowsServiceCollector(WindowsVolumeCollector):
  """Class that defines a Windows service collector."""

  _REGISTRY_FILENAME_SYSTEM = u'C:\\Windows\\System32\\config\\SYSTEM'

  def __init__(self):
    """Initializes the Windows service collector object."""
    super(WindowsServiceCollector, self).__init__()
    self.found_services_key = False

  def _OpenRegistryFile(self, windows_path):
    """Opens the registry file specificed by the Windows path.

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

  def _CollectWindowsServicesFromKey(self, output_writer, services_key):
    """Collects the Windows services from a services Registry key.

    Args:
      output_writer: the output writer object.
      services_key: the services Registry key (instance of pyregf.key).
    """
    print u'\tNumber of entries\t: {0:d}'.format(
        services_key.number_of_sub_keys)
    print u''

    for service_key in services_key.sub_keys:
      print u'{0:s}'.format(service_key.name)

      type_value = service_key.get_value_by_name('Type')
      object_name_string = 'Object name'

      if type_value:
        type_value = type_value.data_as_integer

        if type_value == 0x00000001:
          type_string = 'Kernel device driver'

        elif type_value == 0x00000002:
          type_string = 'File system driver'

        elif type_value == 0x00000004:
          type_string = 'Adapter arguments'

        elif type_value == 0x00000010:
          type_string = 'Stand-alone service'
          object_name_string = 'Account name'
        
        elif type_value == 0x00000020:
          type_string = 'Shared service'
          object_name_string = 'Account name'

        else:
          if type_value == 0x00000110:
            object_name_string = 'Account name'

          type_string = 'Unknown 0x{0:08x}'.format(type_value)

        print u'\tType\t\t\t: {0:s}'.format(type_string)

      display_name_value = service_key.get_value_by_name('DisplayName') 

      if display_name_value:
        if display_name_value.type in [
            RegistryFile.REG_SZ, RegistryFile.REG_EXPAND_SZ]:
          print u'\tDisplay name\t\t: {0:s}'.format(
              display_name_value.data_as_string)

      description_value = service_key.get_value_by_name('Description') 

      if description_value:
        print u'\tDescription\t\t: {0:s}'.format(
            description_value.data_as_string)

      image_path_value = service_key.get_value_by_name('ImagePath') 

      if image_path_value:
        print u'\tExecutable\t\t: {0:s}'.format(image_path_value.data_as_string)

      object_name_value = service_key.get_value_by_name('ObjectName') 

      if object_name_value:
        print u'\t{0:s}\t\t: {1:s}'.format(
            object_name_string, object_name_value.data_as_string)

      start_value = service_key.get_value_by_name('Start')

      if start_value:
        start_value = start_value.data_as_integer

        if start_value == 0x00000000:
          start_string = 'Boot'

        elif start_value == 0x00000001:
          start_string = 'System'

        elif start_value == 0x00000002:
          start_string = 'Automatic'

        elif start_value == 0x00000003:
          start_string = 'On demand'

        elif start_value == 0x00000004:
          start_string = 'Disabled'

        else:
          start_string = 'Unknown 0x{0:08x}'.format(start_value)

        print u'\tStart\t\t\t: {0:s}'.format(start_string)

      print u''

  def CollectWindowsServices(self, output_writer):
    """Collects the Windows services from the SYSTEM Registry file.

    Args:
      output_writer: the output writer object.
    """
    registry_file = self._OpenRegistryFile(
        self._REGISTRY_FILENAME_SYSTEM)

    root_key = registry_file.GetRootKey()

    if root_key:
      for control_set_key in root_key.sub_keys:
        if control_set_key.name.startswith('ControlSet'):
          services_key = control_set_key.get_sub_key_by_name('Services')
          if services_key:
            self.found_services_key = True

            print u'Control set: {0:s}'.format(control_set_key.name)
            self._CollectWindowsServicesFromKey(output_writer, services_key)

    registry_file.Close()


class RegistryFile(object):
  """Class that defines a Windows Registry file."""

  _CLASS_IDENTIFIERS_KEY_PATH = 'Classes\\CLSID'

  REG_NONE = 0
  REG_SZ = 1
  REG_EXPAND_SZ = 2
  REG_BINARY = 3
  REG_DWORD = 4
  REG_DWORD_LITTLE_ENDIAN = 4
  REG_DWORD_BIG_ENDIAN = 5
  REG_LINK = 6
  REG_MULTI_SZ = 7
  REG_RESOURCE_LIST = 8
  REG_FULL_RESOURCE_DESCRIPTOR = 9
  REG_RESOURCE_REQUIREMENT_LIST = 10
  REG_QWORD = 11

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

  def GetRootKey(self):
    """Retrieves the root keys.

    Yields:
      A Registry key (instance of pyregf.key).
    """
    return self._regf_file.get_root_key()


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


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the services information from a SYSTEM '
      ' Registry File (REGF).'))

  args_parser.add_argument(
      'source', nargs='?', action='store', metavar='/mnt/c/',
      default=None, help=('path of the volume containing C:\\Windows or the '
                          'filename of a storage media image containing the '
                          'C:\\Windows directory.'))

  options = args_parser.parse_args()

  if not options.source:
    print u'Source value is missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print u'Unable to open output writer.'
    print u''
    return False

  collector = WindowsServiceCollector()

  if not collector.GetWindowsVolumePathSpec(options.source):
    print (
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source)
    print ''
    return False

  collector.CollectWindowsServices(output_writer)
  output_writer.Close()

  if not collector.found_services_key:
    print u'No services key found.'

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
