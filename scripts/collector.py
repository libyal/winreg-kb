# -*- coding: utf-8 -*-
"""Classes to implement a Windows volume collector."""

from __future__ import print_function
import getpass
import os
import sys

import dfvfs

from dfvfs.credentials import manager as credentials_manager
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.helpers import source_scanner
from dfvfs.helpers import windows_path_resolver
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system

import registry


if dfvfs.__version__ < u'20150704':
  raise ImportWarning(u'collector.py requires dfvfs 20150704 or later.')


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
    self._source_scanner = source_scanner.SourceScanner()
    self._single_file = False
    self._source_path = None
    self._windows_directory = None

  def _GetTSKPartitionIdentifiers(self, scan_node):
    """Determines the TSK partition identifiers.

    Args:
      scan_node: the scan node (instance of dfvfs.ScanNode).

    Returns:
      A list of partition identifiers.

    Raises:
      RuntimeError: if the format of or within the source is not supported or
                    the the scan node is invalid or if the volume for
                    a specific identifier cannot be retrieved.
    """
    if not scan_node or not scan_node.path_spec:
      raise RuntimeError(u'Invalid scan node.')

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(scan_node.path_spec)

    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      print(u'[WARNING] No partitions found.')
      return

    return volume_identifiers

  def _PromptUserForEncryptedVolumeCredential(
      self, scan_context, locked_scan_node, credentials):
    """Prompts the user to provide a credential for an encrypted volume.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      locked_scan_node: the locked scan node (instance of SourceScanNode).
      credentials: the credentials supported by the locked scan node (instance
                   of dfvfs.Credentials).

    Returns:
      A boolean value indicating whether the volume was unlocked.
    """
    # TODO: print volume description.
    if locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
      print(u'Found a BitLocker encrypted volume.')
    else:
      print(u'Found an encrypted volume.')

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append(u'skip')

    print(u'Supported credentials:')
    print(u'')
    for index, name in enumerate(credentials_list):
      print(u'  {0:d}. {1:s}'.format(index, name))
    print(u'')
    print(u'Note that you can abort with Ctrl^C.')
    print(u'')

    result = False
    while not result:
      print(u'Select a credential to unlock the volume: ', end=u'')
      # TODO: add an input reader.
      input_line = sys.stdin.readline()
      input_line = input_line.strip()

      if input_line in credentials_list:
        credential_type = input_line
      else:
        try:
          credential_type = int(input_line, 10)
          credential_type = credentials_list[credential_type]
        except (IndexError, ValueError):
          print(u'Unsupported credential: {0:s}'.format(input_line))
          continue

      if credential_type == u'skip':
        break

      credential_data = getpass.getpass(u'Enter credential data: ')
      print(u'')

      if credential_type == u'key':
        try:
          credential_data = credential_data.decode(u'hex')
        except TypeError:
          print(u'Unsupported credential data.')
          continue

      result = self._source_scanner.Unlock(
          scan_context, locked_scan_node.path_spec, credential_type,
          credential_data)

      if not result:
        print(u'Unable to unlock volume.')
        print(u'')

    return result

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

  def _ScanVolume(self, scan_context, volume_scan_node, windows_path_specs):
    """Scans the volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      windows_path_specs: a list of source path specification (instances
                          of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source
                    is not supported or the the scan node is invalid.
    """
    if not volume_scan_node or not volume_scan_node.path_spec:
      raise RuntimeError(u'Invalid or missing volume scan node.')

    if len(volume_scan_node.sub_nodes) == 0:
      self._ScanVolumeScanNode(
          scan_context, volume_scan_node, windows_path_specs)

    else:
      # Some volumes contain other volume or file systems e.g. BitLocker ToGo
      # has an encrypted and unencrypted volume.
      for sub_scan_node in volume_scan_node.sub_nodes:
        self._ScanVolumeScanNode(
            scan_context, sub_scan_node, windows_path_specs)

  def _ScanVolumeScanNode(
      self, scan_context, volume_scan_node, windows_path_specs):
    """Scans an individual volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      windows_path_specs: a list of source path specification (instances
                          of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source
                    is not supported or the the scan node is invalid.
    """
    if not volume_scan_node or not volume_scan_node.path_spec:
      raise RuntimeError(u'Invalid or missing volume scan node.')

    # Get the first node where where we need to decide what to process.
    scan_node = volume_scan_node
    while len(scan_node.sub_nodes) == 1:
      scan_node = scan_node.sub_nodes[0]

    # The source scanner found an encrypted volume and we need
    # a credential to unlock the volume.
    if scan_node.type_indicator in definitions.ENCRYPTED_VOLUME_TYPE_INDICATORS:
      self._ScanVolumeScanNodeEncrypted(
          scan_context, scan_node, windows_path_specs)

    # The source scanner found Volume Shadow Snapshot which is ignored.
    elif scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      pass

    elif scan_node.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS:
      file_system = resolver.Resolver.OpenFileSystem(scan_node.path_spec)
      if file_system:
        try:
          path_resolver = windows_path_resolver.WindowsPathResolver(
              file_system, scan_node.path_spec.parent)

          result = self._ScanFileSystem(path_resolver)
          if result:
            windows_path_specs.append(scan_node.path_spec)

        finally:
          file_system.Close()

  def _ScanVolumeScanNodeEncrypted(
      self, scan_context, volume_scan_node, windows_path_specs):
    """Scans an encrypted volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      windows_path_specs: a list of source path specification (instances
                          of dfvfs.PathSpec).
    """
    result = not scan_context.IsLockedScanNode(volume_scan_node.path_spec)
    if not result:
      credentials = credentials_manager.CredentialsManager.GetCredentials(
          volume_scan_node.path_spec)

      result = self._PromptUserForEncryptedVolumeCredential(
          scan_context, volume_scan_node, credentials)

    if result:
      self._source_scanner.Scan(
          scan_context, scan_path_spec=volume_scan_node.path_spec)
      self._ScanVolume(scan_context, volume_scan_node, windows_path_specs)

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
    # Note that os.path.exists() does not support Windows device paths.
    if (not source_path.startswith(u'\\\\.\\') and
        not os.path.exists(source_path)):
      raise CollectorError(
          u'No such device, file or directory: {0:s}.'.format(source_path))

    self._source_path = source_path
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(source_path)

    try:
      self._source_scanner.Scan(scan_context)
    except (errors.BackEndError, ValueError) as exception:
      raise RuntimeError(
          u'Unable to scan source with error: {0:s}.'.format(exception))

    self._single_file = False
    if scan_context.source_type == definitions.SOURCE_TYPE_FILE:
      self._single_file = True
      return True

    windows_path_specs = []
    scan_node = scan_context.GetRootScanNode()
    if scan_context.source_type == definitions.SOURCE_TYPE_DIRECTORY:
      windows_path_specs.append(scan_node.path_spec)

    else:
      # Get the first node where where we need to decide what to process.
      while len(scan_node.sub_nodes) == 1:
        scan_node = scan_node.sub_nodes[0]

      # The source scanner found a partition table and we need to determine
      # which partition needs to be processed.
      if scan_node.type_indicator != definitions.TYPE_INDICATOR_TSK_PARTITION:
        partition_identifiers = None

      else:
        partition_identifiers = self._GetTSKPartitionIdentifiers(scan_node)

      if not partition_identifiers:
        self._ScanVolume(scan_context, scan_node, windows_path_specs)

      else:
        for partition_identifier in partition_identifiers:
          location = u'/{0:s}'.format(partition_identifier)
          sub_scan_node = scan_node.GetSubNodeByLocation(location)
          self._ScanVolume(scan_context, sub_scan_node, windows_path_specs)

    if not windows_path_specs:
      raise CollectorError(
          u'No supported file system found in source.')

    file_system_path_spec = windows_path_specs[0]
    self._file_system = resolver.Resolver.OpenFileSystem(file_system_path_spec)

    if file_system_path_spec.type_indicator == definitions.TYPE_INDICATOR_OS:
      mount_point = file_system_path_spec
    else:
      mount_point = file_system_path_spec.parent

    self._path_resolver = windows_path_resolver.WindowsPathResolver(
        self._file_system, mount_point)

    # The source is a directory or single volume storage media image.
    if not self._windows_directory:
      if not self._ScanFileSystem(self._path_resolver):
        return False

    if not self._windows_directory:
      return False

    self._path_resolver.SetEnvironmentVariable(
        u'SystemRoot', self._windows_directory)
    self._path_resolver.SetEnvironmentVariable(
        u'WinDir', self._windows_directory)

    return True

  def OpenFile(self, windows_path):
    """Opens the file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the file.

    Returns:
      The file-like object (instance of dfvfs.FileIO) or None if
      the file does not exist.
    """
    if self._single_file:
      # TODO: check name or move this into WindowsRegistryCollector.
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=self._source_path)
    else:
      path_spec = self._path_resolver.ResolvePath(windows_path)
      if path_spec is None:
        return None

    return resolver.Resolver.OpenFileObject(path_spec)


class CollectorRegistryFileReader(registry.RegistryFileReader):
  """Class that defines the collector-based Windows Registry file reader."""

  def __init__(self, collector):
    """Initializes the Windows Registry file reader.

    Args:
      collector: the Windows volume collector (instance of
                 WindowsVolumeCollector).
    """
    super(CollectorRegistryFileReader, self).__init__()
    self._collector = collector

  def Open(self, windows_path):
    """Opens the Registry file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the Registry file.

    Returns:
      The Registry file (instance of RegistryFile) or None.
    """
    file_object = self._collector.OpenFile(windows_path)
    if file_object is None:
      return None

    registry_file = registry.RegistryFile()
    registry_file.Open(file_object)
    return registry_file


class WindowsRegistryCollector(WindowsVolumeCollector):
  """Class that defines a Windows Registry collector."""

  # TODO: replace by Registry.
  _REGISTRY_FILENAME_SYSTEM = u'%WinDir%\\System32\\config\\SYSTEM'

  def __init__(self):
    """Initializes the Windows Registry collector object."""
    super(WindowsRegistryCollector, self).__init__()
    registry_file_reader = CollectorRegistryFileReader(self)
    self._registry = registry.Registry(registry_file_reader)

  # TODO: improve handling Registry mapping of single file.

  # TODO: replace by Registry.
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

    registry_file = registry.RegistryFile()
    registry_file.Open(file_object)
    return registry_file
