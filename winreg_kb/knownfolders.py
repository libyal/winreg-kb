# -*- coding: utf-8 -*-
"""Windows known folders collector."""

from dfwinreg import registry

from winreg_kb import collector


class KnownFolder(object):
  """Class that defines a known folder.

  Attributes:
    guid: string containing the identifier.
    localized_name: string containing the localized name.
    name: string containing the name.
  """

  def __init__(self, guid, name, localized_name):
    """Initializes a known folder object.

    Args:
      guid: string containing the identifier.
      name: string containing the name.
      localized_name: string containing the localized name.
    """
    super(KnownFolder, self).__init__()
    self.guid = guid
    self.localized_name = localized_name
    self.name = name


class KnownFoldersCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows known folders collector.

  Attributes:
    found_folder_descriptions_key: boolean value to indicate a Known Folder
                                   descriptions Registry key was found.
  """

  DEFAULT_VALUE_NAME = u''

  _FOLDER_DESCRIPTIONS_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\FolderDescriptions')

  def __init__(self):
    """Initializes the collector object."""
    super(KnownFoldersCollector, self).__init__()
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.found_folder_descriptions_key = False

  def _GetValueAsStringFromKey(self, key, value_name, default_value=u''):
    """Retrieves a value as a string from the key.

    Args:
      key: the key object (instance of pyregf.key).
      value_name: string containing the name of the value.
      default_value: optional default value. The default is an empty string.

    Returns:
      The value as a string or the default value if not available.
    """
    if not key:
      return default_value

    value = key.GetValueByName(value_name)
    if not value:
      return default_value

    return value.GetDataAsObject()

  def Collect(self, output_writer):
    """Collects the known folders.

    Args:
      output_writer: the output writer object.
    """
    self.found_folder_descriptions_key = False

    folder_descriptions_key = self._registry.GetKeyByPath(
        self._FOLDER_DESCRIPTIONS_KEY_PATH)
    if not folder_descriptions_key:
      return

    self.found_folder_descriptions_key = True

    for subkey in folder_descriptions_key.GetSubkeys():
      guid = subkey.name.lower()
      name = self._GetValueAsStringFromKey(subkey, u'Name')
      localized_name = self._GetValueAsStringFromKey(
          subkey, u'LocalizedName')

      known_folder = KnownFolder(guid, name, localized_name)
      output_writer.WriteKnownFolder(known_folder)
