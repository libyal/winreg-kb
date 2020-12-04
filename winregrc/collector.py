# -*- coding: utf-8 -*-
"""Windows volume collector."""

from __future__ import unicode_literals

from dfvfs.helpers import command_line as dfvfs_command_line
from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner
from dfvfs.lib import definitions as dfvfs_definitions
from dfvfs.lib import errors as dfvfs_errors
from dfvfs.path import factory as dfvfs_path_spec_factory
from dfvfs.resolver import resolver as dfvfs_resolver

from dfwinreg import interface as dfwinreg_interface
from dfwinreg import creg as dfwinreg_creg
from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry


class CollectorRegistryFileReader(dfwinreg_interface.WinRegistryFileReader):
  """Collector-based Windows Registry file reader."""

  def __init__(self, volume_scanner):
    """Initializes a Windows Registry file reader object.

    Args:
      volume_scanner (dfvfs.WindowsVolumeScanner): Windows volume scanner.
    """
    super(CollectorRegistryFileReader, self).__init__()
    self._volume_scanner = volume_scanner

  def Open(self, path, ascii_codepage='cp1252'):
    """Opens the Windows Registry file specified by the path.

    Args:
      path (str): path of the Windows Registry file. The path is a Windows
          path relative to the root of the file system that contains the
          specific Windows Registry file, such as:
          C:\\Windows\\System32\\config\\SYSTEM
      ascii_codepage (Optional[str]): ASCII string codepage.

    Returns:
      WinRegistryFile: Windows Registry file or None the file does not exist or
          cannot be opened.
    """
    registry_file = None

    file_object = self._volume_scanner.OpenFile(path)
    if file_object:
      try:
        registry_file = dfwinreg_regf.REGFWinRegistryFile(
            ascii_codepage=ascii_codepage)

        registry_file.Open(file_object)
      except IOError:
        registry_file = None

      if not registry_file:
        try:
          registry_file = dfwinreg_creg.CREGWinRegistryFile(
              ascii_codepage=ascii_codepage)

          registry_file.Open(file_object)
        except IOError:
          registry_file = None

      if not registry_file:
        file_object.close()

    return registry_file


class WindowsRegistryCollector(dfvfs_volume_scanner.WindowsVolumeScanner):
  """Windows Registry collector.

  Attributes:
    registry (dfwinreg.WinRegistry): Windows Registry.
  """

  def __init__(self, mediator=None):
    """Initializes a Windows Registry collector.

    Args:
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(WindowsRegistryCollector, self).__init__(mediator=mediator)
    self._single_file = False
    registry_file_reader = CollectorRegistryFileReader(self)
    self.registry = dfwinreg_registry.WinRegistry(
        registry_file_reader=registry_file_reader)

  def IsSingleFileRegistry(self):
    """Determines if the Registry consists of a single file.

    Returns:
      bool: True if the Registry consists of a single file.
    """
    return self._single_file

  def OpenFile(self, windows_path):
    """Opens the file specified by the Windows path.

    Args:
      windows_path (str): Windows path to the file.

    Returns:
      dfvfs.FileIO: file-like object or None if the file does not exist.

    Raises:
      ScannerError: if the scan node is invalid or the scanner does not know
          how to proceed.
    """
    if self._single_file:
      # TODO: check name of single file.
      path_spec = dfvfs_path_spec_factory.Factory.NewPathSpec(
          dfvfs_definitions.TYPE_INDICATOR_OS, location=self._source_path)
      if path_spec is None:
        return None

      return dfvfs_resolver.Resolver.OpenFileObject(path_spec)

    windows_path_upper = windows_path.upper()
    if windows_path_upper.startswith('%USERPROFILE%'):
      if not self._mediator:
        raise dfvfs_errors.ScannerError(
            'Unable to proceed. %UserProfile% found in Windows path but no '
            'mediator to determine which user to select.')

      users_path_spec = self._path_resolver.ResolvePath('\\Users')
      # TODO: handle alternative users path locations
      if users_path_spec is None:
        raise dfvfs_errors.ScannerError(
            'Unable to proceed. %UserProfile% found in Windows path but no '
            'users path found to determine which user to select.')

      users_file_entry = dfvfs_resolver.Resolver.OpenFileEntry(users_path_spec)
      self._mediator.PrintUsersSubDirectoriesOverview(users_file_entry)

      # TODO: list users and determine corresponding windows_path

    return super(WindowsRegistryCollector, self).OpenFile(windows_path)

  def ScanForWindowsVolume(self, source_path, options=None):
    """Scans for a Windows volume.

    Args:
      source_path (str): source path.
      options (Optional[VolumeScannerOptions]): volume scanner options. If None
          the default volume scanner options are used, which are defined in the
          VolumeScannerOptions class.

    Returns:
      bool: True if a Windows volume was found.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within
          the source file is not supported.
    """
    result = super(WindowsRegistryCollector, self).ScanForWindowsVolume(
        source_path, options=options)

    if self._source_type == dfvfs_definitions.SOURCE_TYPE_FILE:
      self._single_file = True
      return True

    return result


class WindowsRegistryCollectorMediator(
    dfvfs_command_line.CLIVolumeScannerMediator):
  """Windows Registry collector mediator."""

  def PrintUsersSubDirectoriesOverview(self, users_file_entry):
    """Prints an overview of the Users sub directories.

    Args:
      users_file_entry (dfvfs.FileEntry): file entry of the Users directory.
    """
    if users_file_entry.IsLink():
      users_file_entry = users_file_entry.GetLinkedFileEntry()

    # TODO: handle missing sub directories

    if users_file_entry:
      column_names = ['Username']
      table_view = dfvfs_command_line.CLITabularTableView(
          column_names=column_names)

      for sub_file_entry in users_file_entry.sub_file_entries:
        if sub_file_entry.IsDirectory():
          table_view.AddRow([sub_file_entry.name])

      self._output_writer.Write('\n')
      # table_view.Write(self._output_writer)
