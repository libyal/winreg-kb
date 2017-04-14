# -*- coding: utf-8 -*-
"""The Windows Registry key and value filters."""

import abc


class BaseWindowsRegistryKeyFilter(object):
  """Windows Registry key filter interface."""

  @property
  def key_paths(self):
    """List of key paths defined by the filter."""
    return []

  @abc.abstractmethod
  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key (dfwinreg.WinRegistryKey): a Windows Registry key.

    Returns:
      bool: True if a match, False otherwise.
    """


class WindowsRegistryKeyPathFilter(BaseWindowsRegistryKeyFilter):
  """Windows Registry key path filter."""

  _CONTROL_SET_PREFIX = (
      u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet')

  # This list must be ordered with most specific matches first.
  _WOW64_PREFIXES = [
      u'HKEY_CURRENT_USER\\Software\\Classes',
      u'HKEY_CURRENT_USER\\Software',
      u'HKEY_LOCAL_MACHINE\\Software\\Classes',
      u'HKEY_LOCAL_MACHINE\\Software']

  def __init__(self, key_path):
    """Initializes a Windows Registry key filter.

    Args:
      key_path (str): key path.
    """
    super(WindowsRegistryKeyPathFilter, self).__init__()

    key_path.rstrip(u'\\')
    self._key_path = key_path

    key_path = key_path.upper()
    self._key_path_upper = key_path

    self._wow64_key_path = None
    self._wow64_key_path_upper = None

    if key_path.startswith(self._CONTROL_SET_PREFIX.upper()):
      self._key_path_prefix, _, self._key_path_suffix = key_path.partition(
          u'CurrentControlSet'.upper())

    else:
      self._key_path_prefix = None
      self._key_path_suffix = None

      # Handle WoW64 Windows Registry key redirection.
      # Also see:
      # https://msdn.microsoft.com/en-us/library/windows/desktop/
      # ms724072%28v=vs.85%29.aspx
      # https://msdn.microsoft.com/en-us/library/windows/desktop/
      # aa384253(v=vs.85).aspx
      wow64_prefix = None
      for key_path_prefix in self._WOW64_PREFIXES:
        if key_path.startswith(key_path_prefix.upper()):
          wow64_prefix = key_path_prefix
          break

      if wow64_prefix:
        key_path_suffix = self._key_path[len(wow64_prefix):]
        if key_path_suffix.startswith(u'\\'):
          key_path_suffix = key_path_suffix[1:]
        self._wow64_key_path = u'\\'.join([
            wow64_prefix, u'Wow6432Node', key_path_suffix])
        self._wow64_key_path_upper = self._wow64_key_path.upper()

  @property
  def key_paths(self):
    """list[str]: key paths defined by the filter."""
    if self._wow64_key_path:
      return [self._key_path, self._wow64_key_path]
    return [self._key_path]

  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key (dfwinreg.WinRegistryKey): a Windows Registry key.

    Returns:
      bool: True if a match, False otherwise.
    """
    key_path = registry_key.path.upper()
    if self._key_path_prefix and self._key_path_suffix:
      if (key_path.startswith(self._key_path_prefix) and
          key_path.endswith(self._key_path_suffix)):

        key_path_segment = key_path[
            len(self._key_path_prefix):-len(self._key_path_suffix)]
        if key_path_segment.startswith(u'ControlSet'.upper()):
          try:
            control_set = int(key_path_segment[10:], 10)
          except ValueError:
            control_set = None

          # TODO: check if control_set is in bounds.
          return control_set is not None

    return (
        key_path == self._key_path_upper or
        key_path == self._wow64_key_path_upper)


class WindowsRegistryKeyPathPrefixFilter(BaseWindowsRegistryKeyFilter):
  """Windows Registry key path prefix filter."""

  def __init__(self, key_path_prefix):
    """Initializes a Windows Registry key filter.

    Args:
      key_path_prefix (str): key path prefix.
    """
    super(WindowsRegistryKeyPathPrefixFilter, self).__init__()
    self._key_path_prefix = key_path_prefix

  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key (dfwinreg.WinRegistryKey): a Windows Registry key.

    Returns:
      bool: True if a match, False otherwise.
    """
    return registry_key.path.startsswith(self._key_path_prefix)


class WindowsRegistryKeyPathSuffixFilter(BaseWindowsRegistryKeyFilter):
  """Windows Registry key path suffix filter."""

  def __init__(self, key_path_suffix):
    """Initializes a Windows Registry key filter.

    Args:
      key_path_prefix (str): key path prefix.
    """
    super(WindowsRegistryKeyPathSuffixFilter, self).__init__()
    self._key_path_suffix = key_path_suffix

  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key (dfwinreg.WinRegistryKey): a Windows Registry key.

    Returns:
      bool: True if a match, False otherwise.
    """
    return registry_key.path.endswith(self._key_path_suffix)


class WindowsRegistryKeyWithValuesFilter(BaseWindowsRegistryKeyFilter):
  """Windows Registry key with values filter."""

  _EMPTY_SET = frozenset()

  def __init__(self, value_names):
    """Initializes a Windows Registry key filter.

    Args:
      value_names (list[str]): value names that should be present in the key.
    """
    super(WindowsRegistryKeyWithValuesFilter, self).__init__()
    self._value_names = frozenset(value_names)

  def Match(self, registry_key):
    """Determines if a Windows Registry key matches the filter.

    Args:
      registry_key (dfwinreg.WinRegistryKey): a Windows Registry key.

    Returns:
      bool: True if a match, False otherwise.
    """
    value_names = frozenset([
        registry_value.name for registry_value in registry_key.GetValues()])

    return self._value_names.issubset(value_names)
