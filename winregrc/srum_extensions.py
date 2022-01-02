# -*- coding: utf-8 -*-
"""System Resource Usage Monitor (SRUM) extension collector."""

from winregrc import interface


class SRUMExtension(object):
  """System Resource Usage Monitor (SRUM) extension.

  Attributes:
    dll_name (str): DLL name.
    guid (str): identifier.
  """

  def __init__(self, guid, dll_name):
    """Initializes a System Resource Usage Monitor (SRUM) extension.

    Args:
      guid (str): identifier.
      dll_name (str): DLL name.
    """
    super(SRUMExtension, self).__init__()
    self.guid = guid
    self.dll_name = dll_name


class SRUMExtensionsCollector(interface.WindowsRegistryKeyCollector):
  """Windows System Resource Usage Monitor (SRUM) extension collector."""

  _SRUM_EXTENSIONS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      'SRUM\\Extensions')

  def Collect(self, registry, output_writer):
    """Collects the SRUM extensions.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the SRUM extensions key was found, False if not.
    """
    srum_extensions_key = registry.GetKeyByPath(self._SRUM_EXTENSIONS_KEY_PATH)
    if not srum_extensions_key:
      return False

    for subkey in srum_extensions_key.GetSubkeys():
      guid = subkey.name.upper()
      dll_name = self._GetValueFromKey(subkey, 'DllName')

      srum_extension = SRUMExtension(guid, dll_name)
      output_writer.WriteSRUMExtension(srum_extension)

    return True
