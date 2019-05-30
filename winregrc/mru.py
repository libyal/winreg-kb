# -*- coding: utf-8 -*-
"""Most Recently Used (MRU) collector."""

from __future__ import unicode_literals

from dtfabric.runtime import data_maps as dtfabric_data_maps

from winregrc import data_format
from winregrc import errors


class MostRecentlyUsedEntry(object):
  """Most Recently Used (MRU) entry.

  Attributes:
    key_path (str): path of the Windows Registry key.
    shell_item_data (bytes): Shell Item data.
    shell_item_list_data (bytes): Shell Item list data.
    string (str): string.
    value_name (str): name of the Windows Registry value.
  """

  def __init__(
      self, key_path=None, shell_item_data=None, shell_item_list_data=None,
      string=None, value_name=None):
    """Initializes a Most Recently Used (MRU) entry.

    Args:
      key_path (Optional[str]): path of the Windows Registry key.
      shell_item_data (Optional[bytes]): Shell Item data.
      shell_item_list_data (Optional[bytes]): Shell Item list data.
      string (Optional[str]): string.
      value_name (Optional[str]): name of the Windows Registry value.
    """
    super(MostRecentlyUsedEntry, self).__init__()
    self.key_path = key_path
    self.shell_item_data = shell_item_data
    self.shell_item_list_data = shell_item_list_data
    self.string = string
    self.value_name = value_name


class MostRecentlyUsedCollector(data_format.BinaryDataFormat):
  """Most Recently Used (MRU) collector.

  Attributes:
    mru_entries (list[MostRecentlyUsedEntry]): most recently used (MRU) entries.
  """

  _DEFINITION_FILE = 'mru.yaml'

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

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Most Recently Used (MRU) collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(MostRecentlyUsedCollector, self).__init__(debug=debug)
    self._output_writer = output_writer
    self.mru_entries = []

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

  def _ProcessKey(self, registry_key):
    """Processes a Windows Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    result = False
    value_names = [
        registry_value.name for registry_value in registry_key.GetValues()]

    if 'MRUList' in value_names:
      if self._ProcessKeyWithMRUListValue(registry_key):
        result = True

    elif 'MRUListEx' in value_names:
      if self._ProcessKeyWithMRUListExValue(registry_key):
        result = True

    for subkey in registry_key.GetSubkeys():
      if self._ProcessKey(subkey):
        result = True

    return result

  def _ProcessKeyWithMRUListValue(self, registry_key):
    """Processes a Windows Registry key that contains a MRUList value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.

    Raises:
      ParseError: if the MRUList value could not be parsed.
    """
    registry_value = registry_key.GetValueByName('MRUList')

    data_type_map = self._GetDataTypeMap('mrulist_entries')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'data_size': len(registry_value.data)})

    try:
      mrulist_entries = self._ReadStructureFromByteStream(
          registry_value.data, 0, data_type_map, 'MRUList entries',
          context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse MRUList entries with error: {0!s}'.format(exception))

    mrulist = set([])
    recovered_mrulist = set([])
    is_recovered = False
    for entry_letter in mrulist_entries:
      if entry_letter == 0:
        is_recovered = True

      entry_letter = chr(entry_letter)

      if is_recovered:
        recovered_mrulist.add(entry_letter)
      else:
        mrulist.add(entry_letter)

    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name in ('MRUList', 'NodeSlot', 'NodeSlots'):
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        self._output_writer.WriteText(description)

      if self._InKeyPaths(registry_key.path, self._SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItem(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItemList(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItem(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItemList(
            registry_key.path, registry_value.name, registry_value.data)

      else:
        self._ProcessMRUEntryString(
            registry_key.path, registry_value.name, registry_value.data)

      result = True

    return result

  def _ProcessKeyWithMRUListExValue(self, registry_key):
    """Processes a Windows Registry key that contains a MRUListEx value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.

    Raises:
      ParseError: if the MRUListEx value could not be parsed.
    """
    # TODO: determine what trailing data is in:
    # HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\
    # ComDlg32\CIDSizeMRU

    registry_value = registry_key.GetValueByName('MRUListEx')

    data_type_map = self._GetDataTypeMap('mrulistex_entries')

    context = dtfabric_data_maps.DataTypeMapContext(values={
        'data_size': len(registry_value.data)})

    try:
      mrulistex_entries = self._ReadStructureFromByteStream(
          registry_value.data, 0, data_type_map, 'MRUListEx entries',
          context=context)
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse MRUListEx entries with error: {0!s}'.format(
              exception))

    mrulistex = set([])
    recovered_mrulistex = set([])
    is_recovered = False
    for entry_number in mrulistex_entries:
      if entry_number == 0:
        is_recovered = True

      if is_recovered:
        recovered_mrulistex.add(entry_number)
      else:
        mrulistex.add(entry_number)

    result = False
    for registry_value in registry_key.GetValues():
      if registry_value.name in ('MRUListEx', 'NodeSlot', 'NodeSlots'):
        continue

      if self._debug:
        description = 'Key: {0:s}\nValue: {1:s}'.format(
            registry_key.path, registry_value.name)
        self._output_writer.WriteText(description)

      if self._InKeyPaths(registry_key.path, self._SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItem(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryShellItemList(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItem(
            registry_key.path, registry_value.name, registry_value.data)

      elif self._InKeyPaths(
          registry_key.path, self._STRING_AND_SHELL_ITEM_LIST_MRU_KEY_PATHS):
        self._ProcessMRUEntryStringAndShellItemList(
            registry_key.path, registry_value.name, registry_value.data)

      else:
        self._ProcessMRUEntryString(
            registry_key.path, registry_value.name, registry_value.data)

      result = True

    return result

  def _ProcessMRUEntryShellItem(self, key_path, value_name, value_data):
    """Processes a shell item MRUEntry.

    Args:
      key_path (str): path of the Windows Registry key.
      value_name (str): name of the Windows Registry value.
      value_data (bytes): Windows Registry value data.
    """
    if self._debug:
      self._output_writer.WriteDebugData('Shell item data', value_data)

    mru_entry = MostRecentlyUsedEntry(
        key_path=key_path, shell_item_data=value_data, value_name=value_name)
    self.mru_entries.append(mru_entry)

  def _ProcessMRUEntryShellItemList(self, key_path, value_name, value_data):
    """Processes a shell item list MRUEntry.

    Args:
      key_path (str): path of the Windows Registry key.
      value_name (str): name of the Windows Registry value.
      value_data (bytes): Windows Registry value data.
    """
    if self._debug:
      self._output_writer.WriteDebugData('Shell item list data', value_data)

    mru_entry = MostRecentlyUsedEntry(
        key_path=key_path, shell_item_list_data=value_data,
        value_name=value_name)
    self.mru_entries.append(mru_entry)

  def _ProcessMRUEntryString(self, key_path, value_name, value_data):
    """Processes a string MRUEntry.

    Args:
      key_path (str): path of the Windows Registry key.
      value_name (str): name of the Windows Registry value.
      value_data (bytes): Windows Registry value data.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
        data_offset += 2
        break

    if self._debug:
      self._output_writer.WriteDebugData(
          'String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      self._output_writer.WriteValue('String', string)

    if self._debug and data_offset < value_data_size:
      self._output_writer.WriteDebugData(
          'Trailing data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(
        key_path=key_path, string=string, value_name=value_name)
    self.mru_entries.append(mru_entry)

  def _ProcessMRUEntryStringAndShellItem(
      self, key_path, value_name, value_data):
    """Processes a string and shell item MRUEntry.

    Args:
      key_path (str): path of the Windows Registry key.
      value_name (str): name of the Windows Registry value.
      value_data (bytes): Windows Registry value data.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
        data_offset += 2
        break

    if self._debug:
      self._output_writer.WriteDebugData(
          'String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      self._output_writer.WriteValue('String', string)

    if data_offset < value_data_size:
      if self._debug:
        self._output_writer.WriteDebugData(
            'Shell item data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(
        key_path=key_path, shell_item_data=value_data[data_offset:],
        string=string, value_name=value_name)
    self.mru_entries.append(mru_entry)

  def _ProcessMRUEntryStringAndShellItemList(
      self, key_path, value_name, value_data):
    """Processes a string and shell item list MRUEntry.

    Args:
      key_path (str): path of the Windows Registry key.
      value_name (str): name of the Windows Registry value.
      value_data (bytes): Windows Registry value data.
    """
    value_data_size = len(value_data)

    data_offset = 0
    for data_offset in range(0, value_data_size, 2):
      if value_data[data_offset:data_offset + 2] == b'\0\0':
        data_offset += 2
        break

    if self._debug:
      self._output_writer.WriteDebugData(
          'String data', value_data[0:data_offset])

    string = value_data[0:data_offset - 2].decode('utf-16-le')

    if self._debug:
      self._output_writer.WriteValue('String', string)

    if data_offset < value_data_size:
      if self._debug:
        self._output_writer.WriteDebugData(
            'Shell item list data', value_data[data_offset:])

    mru_entry = MostRecentlyUsedEntry(
        key_path=key_path, shell_item_list_data=value_data[data_offset:],
        string=string, value_name=value_name)
    self.mru_entries.append(mru_entry)

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects Most Recently Used (MRU) entries.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if a Most Recently Used (MRU) key was found, False if not.
    """
    result = False

    current_user_key = registry.GetKeyByPath('HKEY_CURRENT_USER')
    if current_user_key:
      if self._ProcessKey(current_user_key):
        result = True

    return result
