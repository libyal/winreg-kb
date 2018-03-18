# -*- coding: utf-8 -*-
"""Most Recently Used (MRU) collector."""

from __future__ import unicode_literals

from winregrc import interface


class MostRecentlyUsedEntry(object):
  """Most Recently Used (MRU) entry.

  Attributes:
    shell_item_data (bytes): Shell Item data.
    shell_item_list_data (bytes): Shell Item list data.
    string (str): string.
  """

  def __init__(
      self, shell_item_data=None, shell_item_list_data=None, string=None):
    """Initializes a Most Recently Used (MRU) entry.

    Args:
      shell_item_data (Optional[bytes]): Shell Item data.
      shell_item_list_data (Optional[bytes]): Shell Item list data.
      string (Optional[str]): string.
    """
    super(MostRecentlyUsedEntry, self).__init__()
    self.shell_item_data = shell_item_data
    self.shell_item_list_data = shell_item_list_data
    self.string = string


class MostRecentlyUsedCollector(interface.WindowsRegistryKeyCollector):
  """Most Recently Used (MRU) collector."""

  _OPENSAVE_MRU_KEY_PATH = (
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\ComDlg32\\OpenSaveMRU').upper()

  _SHELL_ITEM_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Local Settings\\Software\\Microsoft\\Windows\\'
       'Shell\\BagMRU'),
      ('HKEY_CURRENT_USER\\Local Settings\\Software\\Microsoft\\Windows\\'
       'ShellNoRoam\\BagMRU'),
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\Shell\\BagMRU',
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\ShellNoRoam\\'
       'BagMRU'),
      ('HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\'
       'Microsoft\\Windows\\Shell\\BagMRU'),
      ('HKEY_CURRENT_USER\\Software\\Classes\\Local Settings\\Software\\'
       'Microsoft\\Windows\\ShellNoRoam\\BagMRU')]

  _SHELL_ITEM_MRU_KEY_PATHS = [
      key_path.upper() for key_path in _SHELL_ITEM_MRU_KEY_PATHS]

  _SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\DesktopStreamMRU'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\ComDlg32\\OpenSavePidlMRU'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\StreamMRU')]

  _SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      key_path.upper() for key_path in _SHELL_ITEM_LIST_MRU_KEY_PATHS]

  _STRING_AND_SHELL_ITEM_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\RecentDocs')]

  _STRING_AND_SHELL_ITEM_MRU_KEY_PATHS = [
      key_path.upper() for key_path in _STRING_AND_SHELL_ITEM_MRU_KEY_PATHS]

  _STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Explorer\\ComDlg32\\LastVisitedPidlMRU')]

  _STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS = [
      key_path.upper()
      for key_path in _STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS]

  def _InKeyPaths(self, key_path, key_paths):
    """Checks if a specific key path is defined in a list of key paths.

    Args:
      key_path (str): Windows Registry key path.
      key_paths (list[str]): list of Windows Registry key paths.

    Returns:
      bool: True if the key path is defined in the list of key paths.
    """
    key_path = key_path.upper()
    for matching_key_path in key_paths:
      if key_path.startswith(matching_key_path):
        return True

    return False

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
    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name in ('MRUList', 'NodeSlot', 'NodeSlots'):
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        output_writer.WriteText(description)

      if self._InKeyPaths(registry_key.path, self._SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItem(registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItemList(registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItem(
            registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItemList(
            registry_value.data, output_writer)

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
    # TODO: determine what trailing data is in:
    # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\
    # ComDlg32\CIDSizeMRU

    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name in ('MRUListEx', 'NodeSlot', 'NodeSlots'):
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        output_writer.WriteText(description)

      if self._InKeyPaths(registry_key.path, self._SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItem(registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItemList(registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItem(
            registry_value.data, output_writer)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItemList(
            registry_value.data, output_writer)

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
    if self._debug:
      output_writer.WriteDebugData('Shell item data', value_data)

    mru_entry = MostRecentlyUsedEntry(shell_item_data=value_data)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryShellItemList(self, value_data, output_writer):
    """Processes a shell item list MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    if self._debug:
      output_writer.WriteDebugData('Shell item list data', value_data)

    mru_entry = MostRecentlyUsedEntry(shell_item_list_data=value_data)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryString(self, value_data, output_writer):
    """Processes a string MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
        data_offset += 2
        break

    if self._debug:
      output_writer.WriteDebugData('String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      output_writer.WriteValue('String', string)

    if self._debug and data_offset < value_data_size:
      output_writer.WriteDebugData('Trailing data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(string=string)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryStringAndShellItem(self, value_data, output_writer):
    """Processes a string and shell item MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
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

    mru_entry = MostRecentlyUsedEntry(
        shell_item_data=value_data[data_offset:], string=string)
    output_writer.WriteMostRecentlyUsedEntry(mru_entry)

  def _ProcessMRUEntryStringAndShellItemList(self, value_data, output_writer):
    """Processes a string and shell item list MRUEntry.

    Args:
      value_data (bytes): Windows Registry value data.
      output_writer (OutputWriter): output writer.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
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

    mru_entry = MostRecentlyUsedEntry(
        shell_item_list_data=value_data[data_offset:], string=string)
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
