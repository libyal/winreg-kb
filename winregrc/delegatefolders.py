# -*- coding: utf-8 -*-
"""Windows delegate folders collector."""

from winregrc import interface


class DelegateFolder(object):
  """Delegate folder.

  Attributes:
    identifier (str): identifier.
    name (str): name.
    namespace (str): namespace.
  """

  def __init__(self, identifier, name, namespace):
    """Initializes a delegate folder.

    Args:
      identifier (str): identifier.
      name (str): name.
      namespace (str): namespace.
    """
    super(DelegateFolder, self).__init__()
    self.identifier = identifier
    self.name = name
    self.namespace = namespace


class DelegateFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Windows delegate folders collector."""

  _EXPLORER_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer')

  def _CollectDelegateFolders(self, delegate_folders_key, namespace):
    """Collects Windows delegate folders.

    Args:
      delegate_folders_key (dfwinreg.WinRegistryKey): delegate folders Windows
          Registry key.
      namespace (str): namespace.

    Yields:
      DelegateFolder: a delegate folder.
    """
    for subkey in delegate_folders_key.GetSubkeys():
      name = self._GetValueFromKey(subkey, '')
      yield DelegateFolder(subkey.name, name, namespace)

  def Collect(self, registry):
    """Collects Windows delegate folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      DelegateFolder: a delegate folder.
    """
    explorer_key = registry.GetKeyByPath(self._EXPLORER_KEY_PATH)
    if explorer_key:
      for subkey in explorer_key.GetSubkeys():
        delegate_folders_key = subkey.GetSubkeyByPath(
            'NameSpace\\DelegateFolders')
        if delegate_folders_key:
          yield from self._CollectDelegateFolders(
              delegate_folders_key, subkey.name)
