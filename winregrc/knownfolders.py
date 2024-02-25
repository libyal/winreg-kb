# -*- coding: utf-8 -*-
"""Windows known folders collector."""

from winregrc import interface


class KnownFolder(object):
  """Known folder.

  Attributes:
    identifier (str): identifier.
    localized_name (str): localized name.
    name (str): name.
  """

  def __init__(self, identifier, name, localized_name):
    """Initializes a known folder.

    Args:
      identifier (str): identifier.
      name (str): name.
      localized_name (str): localized name.
    """
    super(KnownFolder, self).__init__()
    self.identifier = identifier
    self.localized_name = localized_name
    self.name = name


class KnownFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Windows known folders collector."""

  _FOLDER_DESCRIPTIONS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\FolderDescriptions')

  def _CollectKnownFolders(self, folder_descriptions_key):
    """Collects Windows known folders.

    Args:
      folder_descriptions_key (dfwinreg.WinRegistryKey): folder descriptions
          Windows Registry key.

    Yields:
      KnownFolder: a known folder.
    """
    for subkey in folder_descriptions_key.GetSubkeys():
      identifier = subkey.name.lower()
      name = self._GetValueFromKey(subkey, 'Name')
      localized_name = self._GetValueFromKey(subkey, 'LocalizedName')

      yield KnownFolder(identifier, name, localized_name)

  def Collect(self, registry):
    """Collects Windows known folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      KnownFolder: a known folder.
    """
    folder_descriptions_key = registry.GetKeyByPath(
        self._FOLDER_DESCRIPTIONS_KEY_PATH)
    if folder_descriptions_key:
      yield from self._CollectKnownFolders(folder_descriptions_key)
