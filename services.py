#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the drivers and services from the SYSTEM
# Registry file (REGF)
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
import stat
import sys

import dfvfs
import pyregf

from dfvfs.lib import definitions
from dfvfs.helpers import source_scanner
from dfvfs.helpers import windows_path_resolver
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system


if dfvfs.__version__ < '20140727':
  raise ImportWarning('shellfolder.py requires dfvfs 20140727 or later.')

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


class WindowsServiceCollector(WindowsVolumeCollector):
  """Class that defines a Windows service collector."""

  _REGISTRY_FILENAME_SYSTEM = u'%WinDir%\\System32\\config\\SYSTEM'

  def __init__(self):
    """Initializes the Windows service collector object."""
    super(WindowsServiceCollector, self).__init__()
    self.found_services_key = False

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
      type_value = service_key.get_value_by_name('Type')
      if type_value:
        type_value = type_value.data_as_integer

      display_name_value = service_key.get_value_by_name('DisplayName') 
      if display_name_value:
        if display_name_value.type in [
            RegistryFile.REG_SZ, RegistryFile.REG_EXPAND_SZ]:
          display_name_value = display_name_value.data_as_string
        else:
          display_name_value = None

      description_value = service_key.get_value_by_name('Description') 
      if description_value:
        description_value = description_value.data_as_string

      image_path_value = service_key.get_value_by_name('ImagePath') 
      if image_path_value:
        image_path_value = image_path_value.data_as_string

      object_name_value = service_key.get_value_by_name('ObjectName') 
      if object_name_value:
        object_name_value = object_name_value.data_as_string

      start_value = service_key.get_value_by_name('Start')
      if start_value:
        start_value = start_value.data_as_integer

      windows_service = WindowsService(
          service_key.name, type_value, display_name_value, description_value,
          image_path_value, object_name_value, start_value)
      output_writer.WriteWindowsService(windows_service)

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

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service: the Windows service (instance of WindowsService).
    """
    print u'{0:s}'.format(service.name)

    if service.service_type:
      print u'\tType\t\t\t: {0:s}'.format(service.GetServiceTypeDescription())

    if service.display_name:
      print u'\tDisplay name\t\t: {0:s}'.format(service.display_name)

    if service.description:
      print u'\tDescription\t\t: {0:s}'.format(service.description)

    if service.image_path:
      print u'\tExecutable\t\t: {0:s}'.format(service.image_path)

    if service.object_name:
      print u'\t{0:s}\t\t: {1:s}'.format(
          service.GetObjectNameDescription(), service.object_name)

    if service.start_value is not None:
      print u'\tStart\t\t\t: {0:s}'.format(service.GetStartValueDescription())

    print u''


class WindowsService(object):
  """Class that defines a Windows service."""

  def __init__(self, name, service_type, display_name, description, image_path,
               object_name, start_value):
    """Initializes the Windows service object.

    Args:
      name: the name.
      service_type: the service type.
      display_name: the display name.
      description: the service description.
      image_path: the image path.
      object_name: the object name
      start_value: the start value.
    """
    super(WindowsService, self).__init__()
    self.description = description
    self.display_name = display_name
    self.image_path = image_path
    self.name = name
    self.object_name = object_name
    self.service_type = service_type
    self.start_value = start_value

  def GetObjectNameDescription(self):
    """Retrieves the object name as a descriptive string."""
    if self.service_type == 0x00000010:
      return u'Account name'
        
    elif self.service_type == 0x00000020:
      return u'Account name'

    elif self.service_type == 0x00000110:
      return u'Account name'

    return u'Object name'

  def GetServiceTypeDescription(self):
    """Retrieves the service type as a descriptive string."""
    if self.service_type == 0x00000001:
      return u'Kernel device driver'

    elif self.service_type == 0x00000002:
      return u'File system driver'

    elif self.service_type == 0x00000004:
      return u'Adapter arguments'

    elif self.service_type == 0x00000010:
      return u'Stand-alone service'
        
    elif self.service_type == 0x00000020:
      return u'Shared service'

    return u'Unknown 0x{0:08x}'.format(self.service_type)

  def GetStartValueDescription(self):
    """Retrieves the start value as a descriptive string."""
    if self.start_value == 0x00000000:
      return u'Boot'

    elif self.start_value == 0x00000001:
      return u'System'

    elif self.start_value == 0x00000002:
      return u'Automatic'

    elif self.start_value == 0x00000003:
      return u'On demand'

    elif self.start_value == 0x00000004:
      return u'Disabled'

    return u'Unknown 0x{0:08x}'.format(self.start_value)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the services information from a SYSTEM '
      'Registry File (REGF).'))

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
    print u''
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
