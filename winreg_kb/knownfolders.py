# -*- coding: utf-8 -*-
"""Windows known folders collector."""

from dfwinreg import registry

from winreg_kb import collector


class KnownFolder(object):
  """Class that defines a known folder.

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


class KnownFoldersCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows known folders collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

  _FOLDER_DESCRIPTIONS_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\FolderDescriptions')

  def __init__(self, debug=False, mediator=None):
    """Initializes a Windows known folders collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(KnownFoldersCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  def _GetValueAsStringFromKey(self, key, value_name, default_value=u''):
    """Retrieves a value as a string from the key.

    Args:
      key (dfwinreg.WinRegistryKey): Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
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
      output_writer (OutputWriter): output writer.
    """
    self.key_found = False

    folder_descriptions_key = self._registry.GetKeyByPath(
        self._FOLDER_DESCRIPTIONS_KEY_PATH)
    if not folder_descriptions_key:
      return

    self.key_found = True

    for subkey in folder_descriptions_key.GetSubkeys():
      guid = subkey.name.lower()
      name = self._GetValueAsStringFromKey(subkey, u'Name')
      localized_name = self._GetValueAsStringFromKey(
          subkey, u'LocalizedName')

      known_folder = KnownFolder(guid, name, localized_name)
      output_writer.WriteKnownFolder(known_folder)
