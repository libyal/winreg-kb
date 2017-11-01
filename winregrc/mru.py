# -*- coding: utf-8 -*-
"""Most Recently Used (MRU) collector."""

from __future__ import unicode_literals

from winregrc import interface


class MostRecentlyUsedEntry(object):
  """Most Recently Used (MRU) entry.

  Attributes:
    string (str): string.
  """

  def __init__(self, string):
    """Initializes a Most Recently Used (MRU) entry.

    Args:
      string (str): string.
    """
    super(MostRecentlyUsedEntry, self).__init__()
    self.string = string


class MostRecentlyUsedCollector(interface.WindowsRegistryKeyCollector):
  """Most Recently Used (MRU) collector."""

  _BAG_MRU_KEY_PATHS = [
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Shell\\BagMRU',
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\ShellNoRoam\\'
       'BagMRU'),
      ('HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\'
       'Microsoft\\Windows\\Shell\\BagMRU'),
      ('HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\'
       'Microsoft\\Windows\\ShellNoRoam\\BagMRU')]

  _BAG_MRU_KEY_PATHS = [key_path.upper() for key_path in _BAG_MRU_KEY_PATHS]

  _RECENT_DOCS_KEY_PATH = (
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\RecentDocs').upper()

  _SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\DesktopStreamMRU'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\ComDlg32\\OpenSavePidlMRU'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\StreamMRU')]

  _SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      key_path.upper() for key_path in _SHELL_ITEM_LIST_MRU_KEY_PATHS]

  _STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\ComDlg32\\LastVisitedPidlMRU')]

  _STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      key_path.upper() for key_path in _SHELL_ITEM_LIST_MRU_KEY_PATHS]

  def _ProcessKey(self, registry_key, output_writer):
    """Processes a Windows Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    result = False
    value_names = [
        registry_value.name for registry_value in registry_key.GetValues()]

    if 'MRUList' in value_names:
      if self._ProcessKeyWithMRUListValue(registry_key, output_writer):
        result = True

    elif 'MRUListEx' in value_names:
      if self._ProcessKeyWithMRUListExValue(registry_key, output_writer):
        result = True

    for subkey in registry_key.GetSubkeys():
      if self._ProcessKey(subkey, output_writer):
        result = True

    return result

  def _ProcessKeyWithMRUListValue(self, registry_key, output_writer):
    """Processes a Windows Registry key that contains a MRUList value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    key_path = registry_key.path.upper()

    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name == 'MRUList':
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        output_writer.WriteDebugData(description, registry_value.data)

      is_bag_mru_key = False
      for bag_mru_key_path in self._BAG_MRU_KEY_PATHS:
        if key_path.startswith(bag_mru_key_path):
          is_bag_mru_key = True

      if is_bag_mru_key:
        self._ProcessMRUEntryShellItem(registry_value.data, output_writer)

      elif key_path in self._SHELL_ITEM_LIST_MRU_KEY_PATHS:
        self._ProcessMRUEntryShellItemList(registry_value.data, output_writer)

      else:
        self._ProcessMRUEntryString(registry_value.data, output_writer)

      result = True

    return result

  def _ProcessKeyWithMRUListExValue(self, registry_key, output_writer):
    """Processes a Windows Registry key that contains a MRUListEx value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    key_path = registry_key.path.upper()

    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name == 'MRUListEx':
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        output_writer.WriteText(description)

      is_bag_mru_key = False
      for bag_mru_key_path in self._BAG_MRU_KEY_PATHS:
        if key_path.startswith(bag_mru_key_path):
          is_bag_mru_key = True

      if is_bag_mru_key:
        self._ProcessMRUEntryShellItem(registry_value.data, output_writer)

      elif key_path in self._SHELL_ITEM_LIST_MRU_KEY_PATHS:
        self._ProcessMRUEntryShellItemList(registry_value.data, output_writer)

      elif key_path.startswith(self._RECENT_DOCS_KEY_PATH):
        self._ProcessMRUEntryStringAndShellItem(
            registry_value.data, output_writer)

      elif key_path in self._STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS:
        self._ProcessMRUEntryShellItemList(registry_value.data, output_writer)

      else:
        self._ProcessMRUEntryString(registry_value.data, output_writer)

      result = True

    return result

  def _ProcessMRUEntryShellItem(self, value_data, output_writer):
    """Processes a shell item MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)
    result = True

    if self._debug:
      output_writer.WriteDebugData('Shell item data', value_data)

  def _ProcessMRUEntryShellItemList(self, value_data, output_writer):
    """Processes a shell item list MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)
    result = True

    if self._debug:
      output_writer.WriteDebugData('Shell item list data', value_data)

  def _ProcessMRUEntryString(self, value_data, output_writer):
    """Processes a string MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)
    result = True

    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == '\0\0':
        data_offset += 2
        break

    if self._debug:
      output_writer.WriteDebugData('String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      output_writer.WriteValue('String', string)

    if self._debug and data_offset < value_data_size:
      output_writer.WriteDebugData('Trailing data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(string)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryStringAndShellItem(self, value_data, output_writer):
    """Processes a string and shell item MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)
    result = True

    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == '\0\0':
        data_offset += 2
        break

    if self._debug:
      output_writer.WriteDebugData('String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      output_writer.WriteValue('String', string)

    if data_offset < value_data_size:
      if self._debug:
        output_writer.WriteDebugData(
            'Shell item data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(string)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryStringAndShellItemList(self, value_data, output_writer):
    """Processes a string and shell item list MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)
    result = True

    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == '\0\0':
        data_offset += 2
        break

    if self._debug:
      output_writer.WriteDebugData('String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      output_writer.WriteValue('String', string)

    if data_offset < value_data_size:
      if self._debug:
        output_writer.WriteDebugData(
            'Shell item list data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(string)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def Collect(self, registry, output_writer):
    """Collects Most Recently Used (MRU) entries.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    result = False

    current_user_key = registry.GetKeyByPath('HKEY_CURRENT_USER')
    if current_user_key:
      if self._ProcessKey(current_user_key, output_writer):
        result = True

    return result
