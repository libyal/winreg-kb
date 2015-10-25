# -*- coding: utf-8 -*-
"""Classes to provide a uniform way to access the Windows Registry."""

import abc

import pyregf

# TODO: implement dfvfs_pyregf
# TODO: wrap key to hide implementation specifics.


if pyregf.get_version() < u'20130716':
  raise ImportWarning(u'registry_file.py requires pyregf 20130716 or later.')


REG_NONE = 0
REG_SZ = 1
REG_EXPAND_SZ = 2
REG_BINARY = 3
REG_DWORD = 4
REG_DWORD_LITTLE_ENDIAN = 4
REG_DWORD_BIG_ENDIAN = 5
REG_LINK = 6
REG_MULTI_SZ = 7
REG_RESOURCE_LIST = 8
REG_FULL_RESOURCE_DESCRIPTOR = 9
REG_RESOURCE_REQUIREMENT_LIST = 10
REG_QWORD = 11


class WinRegistryFile(object):
  """Class that defines a Windows Registry file."""

  def __init__(self, ascii_codepage=u'cp1252'):
    """Initializes the Windows Registry file.

    Args:
      ascii_codepage: optional ASCII string codepage. The default is cp1252
                      (or windows-1252).
    """
    super(WinRegistryFile, self).__init__()
    self._file_object = None
    self._regf_file = pyregf.file()
    self._regf_file.set_ascii_codepage(ascii_codepage)

  def Close(self):
    """Closes the Windows Registry file."""
    self._regf_file.close()
    self._file_object.close()
    self._file_object = None

  def GetKeyByPath(self, key_path):
    """Retrieves the key for a specific path.

    Args:
      key_path: the Registry key path.

    Returns:
      A Registry key (instance of WinRegistryKey) or None if not available.
    """
    return self._regf_file.get_key_by_path(key_path)

  def GetRootKey(self):
    """Retrieves the root keys.

    Yields:
      A Registry key (instance of WinRegistryKey).
    """
    return self._regf_file.get_root_key()

  def Open(self, file_object):
    """Opens the Windows Registry file using a file-like object.

    Args:
      file_object: the file-like object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    # TODO: detect file type.
    self._file_object = file_object
    self._regf_file.open_file_object(self._file_object)
    return True


class WinRegistryFileMapping(object):
  """Class that defines a Windows Registry file mapping.

  Attributes:
    key_path_prefix: the Registry key path prefix.
    windows_path: the Windows path to the Registry file.
  """

  def __init__(self, key_path_prefix, windows_path):
    """Initializes the Windows Registry file mapping.

    Args:
      key_path_prefix: the Registry key path prefix.
      windows_path: the Windows path to the Registry file.
    """
    super(WinRegistryFileMapping, self).__init__()
    self.key_path_prefix = key_path_prefix.upper()
    self.windows_path = windows_path


class WinRegistryFileReader(object):
  """Class that defines the Windows Registry file reader interface."""

  @abc.abstractmethod
  def Open(self, windows_path, ascii_codepage=u'cp1252'):
    """Opens the Registry file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the Registry file.
      ascii_codepage: optional ASCII string codepage. The default is cp1252
                      (or windows-1252).

    Returns:
      The Registry file (instance of WinRegistryFile) or None.
    """


class WinRegistryKey(object):
  """Class that defines a Windows Registry key."""

  def __init__(self):
    """Initializes the Windows Registry key."""
    super(WinRegistryKey, self).__init__()
    self._regf_key = None


class WinRegistry(object):
  """Class that defines a Windows Registry."""

  _PATH_SEPARATOR = u'\\'

  _REGISTRY_FILE_MAPPINGS_9X = [
      WinRegistryFileMapping(
          u'HKEY_LOCAL_MACHINE',
          u'%SystemRoot%\\SYSTEM.DAT'),
      WinRegistryFileMapping(
          u'HKEY_USERS',
          u'%SystemRoot%\\USER.DAT'),
  ]

  _REGISTRY_FILE_MAPPINGS_NT = [
      WinRegistryFileMapping(
          u'HKEY_CURRENT_USER',
          u'%UserProfile%\\NTUSER.DAT'),
      WinRegistryFileMapping(
          u'HKEY_CURRENT_USER\\Software\\Classes',
          u'%UserProfile%\\AppData\\Local\\Microsoft\\Windows\\UsrClass.dat'),
      WinRegistryFileMapping(
          u'HKEY_CURRENT_USER\\Software\\Classes',
          (u'%UserProfile%\\Local Settings\\Application Data\\Microsoft\\'
           u'Windows\\UsrClass.dat')),
      WinRegistryFileMapping(
          u'HKEY_LOCAL_MACHINE\\SAM',
          u'%SystemRoot%\\System32\\config\\SAM'),
      WinRegistryFileMapping(
          u'HKEY_LOCAL_MACHINE\\Security',
          u'%SystemRoot%\\System32\\config\\SECURITY'),
      WinRegistryFileMapping(
          u'HKEY_LOCAL_MACHINE\\Software',
          u'%SystemRoot%\\System32\\config\\SOFTWARE'),
      WinRegistryFileMapping(
          u'HKEY_LOCAL_MACHINE\\System',
          u'%SystemRoot%\\System32\\config\\SYSTEM'),
  ]

  _ROOT_KEY_ALIASES = {
      u'HKCC': u'HKEY_CURRENT_CONFIG',
      u'HKCR': u'HKEY_CLASSES_ROOT',
      u'HKCU': u'HKEY_CURRENT_USER',
      u'HKLM': u'HKEY_LOCAL_MACHINE',
      u'HKU': u'HKEY_USERS',
  }

  _ROOT_KEYS = frozenset([
      u'HKEY_CLASSES_ROOT',
      u'HKEY_CURRENT_CONFIG',
      u'HKEY_CURRENT_USER',
      u'HKEY_DYN_DATA',
      u'HKEY_LOCAL_MACHINE',
      u'HKEY_PERFORMANCE_DATA',
      u'HKEY_USERS',
  ])

  # TODO: add support for HKEY_USERS.
  _VIRTUAL_KEYS = [
      (u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet',
       u'_GetCurrentControlSet')]

  def __init__(self, registry_file_reader, ascii_codepage=u'cp1252'):
    """Initializes the Windows Registry object.

    Args:
      registry_file_reader: the Registry file reader (instance of
                            WinRegistryFileReader).
      ascii_codepage: optional ASCII string codepage. The default is cp1252
                      (or windows-1252).
    """
    super(WinRegistry, self).__init__()
    self._ascii_codepage = ascii_codepage
    self._registry_file_reader = registry_file_reader
    self._registry_files = {}

  def __del__(self):
    """Cleans up the Windows Registry object."""
    for key_path_prefix, registry_file in iter(self._registry_files.items()):
      self._registry_files[key_path_prefix] = None
      if registry_file:
        registry_file.Close()

  def _GetCachedFileByPath(self, safe_key_path):
    """Retrieves a cached Registry file for a specific path.

    Args:
      safe_key_path: the Registry key path, in upper case with a resolved
                     root key alias.

    Returns:
      A tuple of the key path prefix and the corresponding Registry file object
      (instance of WinRegistryFile) or None if not available.
    """
    longest_key_path_prefix = u''
    longest_key_path_prefix_length = len(longest_key_path_prefix)
    for key_path_prefix in self._registry_files.iterkeys():
      if safe_key_path.startswith(key_path_prefix):
        key_path_prefix_length = len(key_path_prefix)
        if key_path_prefix_length > longest_key_path_prefix_length:
          longest_key_path_prefix = key_path_prefix
          longest_key_path_prefix_length = key_path_prefix_length

    if not longest_key_path_prefix:
      return None, None

    registry_file = self._registry_files.get(longest_key_path_prefix, None)
    return longest_key_path_prefix, registry_file

  def _GetCurrentControlSet(self):
    """Virtual key callback to determine the current control set.

    Returns:
      The resolved key path for the current control set key or
      None if unable to resolve.
    """
    select_key_path = u'HKEY_LOCAL_MACHINE\\System\\Select'
    select_key = self.GetKeyByPath(select_key_path)
    if not select_key:
      return

    # TODO: wrap key implementation.
    current_value = select_key.get_value_by_name(u'Current')
    # TODO: add support for fallback.
    if not current_value:
      return

    # TODO: wrap value implementation.
    control_set = current_value.get_data_as_integer()
    # TODO: check if control set is 0.
    return u'HKEY_LOCAL_MACHINE\\System\\ControlSet{0:03d}'.format(control_set)

  def _GetFileByPath(self, safe_key_path):
    """Retrieves the Registry file for a specific path.

    Args:
      safe_key_path: the Registry key path, in upper case with a resolved
                     root key alias.

    Returns:
      A tuple of the key path prefix and the corresponding Registry file object
      (instance of WinRegistryFile) or None if not available.
    """
    # TODO: handle HKEY_USERS in both 9X and NT.

    key_path_prefix, registry_file = self._GetCachedFileByPath(safe_key_path)
    if not registry_file:
      for mapping in self._GetFileMappingsByPath(safe_key_path):
        registry_file = self._registry_file_reader.Open(
            mapping.windows_path, ascii_codepage=self._ascii_codepage)
        if registry_file:
          if not key_path_prefix:
            key_path_prefix = mapping.key_path_prefix

          # Note make sure the key path prefix is stored in upper case.
          self._registry_files[key_path_prefix] = registry_file
          break

    return key_path_prefix, registry_file

  def _GetFileMappingsByPath(self, safe_key_path):
    """Retrieves the Registry file mappings for a specific path.

    Args:
      safe_key_path: the Registry key path, in upper case with a resolved
                     root key alias.

    Yields:
      Registry file mapping objects (instances of WinRegistryFileMapping).
    """
    candidate_mappings = []
    for mapping in self._REGISTRY_FILE_MAPPINGS_NT:
      if safe_key_path.startswith(mapping.key_path_prefix):
        candidate_mappings.append(mapping)

    # Sort the candidate mappings by longest (most specific) match first.
    candidate_mappings.sort(
        key=lambda mapping: len(mapping.key_path_prefix), reverse=True)
    for mapping in candidate_mappings:
      yield mapping

  def GetKeyByPath(self, key_path):
    """Retrieves the key for a specific path.

    Args:
      key_path: the Registry key path.

    Returns:
      A Registry key (instance of WinRegistryKey) or None if not available.

    Raises:
      RuntimeError: if the root key is not supported.
    """
    root_key_path, _, key_path = key_path.partition(self._PATH_SEPARATOR)

    # Resolve a root key alias.
    root_key_path = self._ROOT_KEY_ALIASES.get(root_key_path, root_key_path)

    if root_key_path not in self._ROOT_KEYS:
      raise RuntimeError(u'Unsupported root key: {0:s}'.format(root_key_path))

    key_path = self._PATH_SEPARATOR.join([root_key_path, key_path])
    safe_key_path = key_path.upper()

    key_path_prefix, registry_file = self._GetFileByPath(safe_key_path)
    if not registry_file:
      return

    if not safe_key_path.startswith(key_path_prefix):
      raise RuntimeError(u'Key path prefix mismatch.')

    for virtual_key_path, virtual_key_callback in self._VIRTUAL_KEYS:
      if key_path.startswith(virtual_key_path):
        callback_function = getattr(self, virtual_key_callback)
        resolved_key_path = callback_function()
        if not resolved_key_path:
          raise RuntimeError(u'Unable to resolve virtual key: {0:s}.'.format(
              virtual_key_path))

        virtual_key_path_length = len(virtual_key_path)
        if key_path[virtual_key_path_length] == self._PATH_SEPARATOR:
          virtual_key_path_length += 1

        key_path = self._PATH_SEPARATOR.join([
            resolved_key_path, key_path[virtual_key_path_length:]])

    key_path = key_path[len(key_path_prefix):]
    return registry_file.GetKeyByPath(key_path)
