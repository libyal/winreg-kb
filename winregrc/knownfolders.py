# -*- coding: utf-8 -*-
"""Windows known folders collector."""

from winregrc import interface


class KnownFolder(object):
  """Known folder.

  Attributes:
    guid (str): identifier.
    localized_name (str): localized name.
    name (str): name.
  """

  def __init__(self, guid, name, localized_name):
    """Initializes a known folder.

    Args:
      guid (str): identifier.
      name (str): name.
      localized_name (str): localized name.
    """
    super(KnownFolder, self).__init__()
    self.guid = guid
    self.localized_name = localized_name
    self.name = name


class KnownFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Windows known folders collector."""

  _FOLDER_DESCRIPTIONS_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\FolderDescriptions')

  def Collect(self, registry, output_writer):
    """Collects the known folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the known folders key was found, False if not.
    """
    folder_descriptions_key = registry.GetKeyByPath(
        self._FOLDER_DESCRIPTIONS_KEY_PATH)
    if not folder_descriptions_key:
      return False

    for subkey in folder_descriptions_key.GetSubkeys():
      guid = subkey.name.lower()
      name = self._GetValueAsStringFromKey(subkey, u'Name')
      localized_name = self._GetValueAsStringFromKey(
          subkey, u'LocalizedName')

      known_folder = KnownFolder(guid, name, localized_name)
      output_writer.WriteKnownFolder(known_folder)

    return True
