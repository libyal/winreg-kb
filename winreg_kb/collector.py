# -*- coding: utf-8 -*-
"""Classes to implement a Windows volume collector."""

import dfvfs
import dfwinreg

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner
from dfvfs.lib import definitions as dfvfs_definitions
from dfvfs.path import factory as dfvfs_path_spec_factory
from dfvfs.resolver import resolver as dfvfs_resolver
from dfwinreg import interface as dfwinreg_interface
from dfwinreg import regf as dfwinreg_regf


if dfvfs.__version__ < u'20160306':
  raise ImportWarning(u'collector.py requires dfvfs 20160306 or later.')

if dfwinreg.__version__ < u'20151026':
  raise ImportWarning(u'collector.py requires dfwinreg 20151026 or later.')


class WindowsVolumeCollector(dfvfs_volume_scanner.WindowsVolumeScanner):
  """Class that defines a Windows volume collector."""

  def __init__(self, mediator=None):
    """Initializes the collector object.

    Args:
      mediator: a volume scanner mediator (instance of
                VolumeScannerMediator) or None.
    """
    super(WindowsVolumeCollector, self).__init__(mediator=mediator)
    self._single_file = False

  def OpenFile(self, windows_path):
    """Opens the file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the file.

    Returns:
      The file-like object (instance of dfvfs.FileIO) or None if
      the file does not exist.
    """
    if not self._single_file:
      return super(WindowsVolumeCollector, self).OpenFile(windows_path)

    # TODO: check name of single file.
    path_spec = dfvfs_path_spec_factory.Factory.NewPathSpec(
        dfvfs_definitions.TYPE_INDICATOR_OS, location=self._source_path)
    if path_spec is None:
      return

    return dfvfs_resolver.Resolver.OpenFileObject(path_spec)

  def ScanForWindowsVolume(self, source_path):
    """Scans for a Windows volume.

    Args:
      source_path: a string containing the source path.

    Returns:
      A boolean value indicating if a Windows volume was found.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
                    is not a file or directory, or if the format of or within
                    the source file is not supported.
    """
    result = super(WindowsVolumeCollector, self).ScanForWindowsVolume(
        source_path)
    if not result:
      return False

    if self._source_type == dfvfs_definitions.SOURCE_TYPE_FILE:
      self._single_file = True

    return True


class CollectorRegistryFileReader(dfwinreg_interface.WinRegistryFileReader):
  """Class that defines the collector-based Windows Registry file reader."""

  def __init__(self, volume_scanner):
    """Initializes the Windows Registry file reader object.

    Args:
      volume_scanner: the Windows volume scanner (instance of
                      WindowsVolumeCollector).
    """
    super(CollectorRegistryFileReader, self).__init__()
    self._volume_scanner = volume_scanner

  def Open(self, path, ascii_codepage=u'cp1252'):
    """Opens the Windows Registry file specificed by the path.

    Args:
      path: string containing the path of the Windows Registry file. The path
            is a Windows path relative to the root of the file system that
            contains the specfic Windows Registry file. E.g.
            C:\\Windows\\System32\\config\\SYSTEM
      ascii_codepage: optional ASCII string codepage.

    Returns:
      The Windows Registry file (instance of WinRegistryFile) or None.
    """
    file_object = self._volume_scanner.OpenFile(path)
    if file_object is None:
      return

    registry_file = dfwinreg_regf.REGFWinRegistryFile(
        ascii_codepage=ascii_codepage)

    try:
      registry_file.Open(file_object)
    except IOError:
      file_object.close()
      return

    return registry_file
