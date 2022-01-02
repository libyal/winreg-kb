# -*- coding: utf-8 -*-
"""Environment variables collector."""

from winregrc import interface


class EnvironmentVariable(object):
  """Environment variable.

  Attributes:
    name (str): name.
    value (str): value.
  """

  def __init__(self, name, value):
    """Initializes an environment variable.

    Args:
      name (str): name.
      value (str): value.
    """
    super(EnvironmentVariable, self).__init__()
    self.name = name
    self.value = value


class EnvironmentVariablesCollector(interface.WindowsRegistryKeyCollector):
  """Environment variables collector."""

  _ENVIRONMENT_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\'
      'Session Manager\\Environment')

  _PROFILELIST_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      'ProfileList')

  _WINDOWS_CURRENTVERSION_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion')

  _WINDOWS_NT_CURRENTVERSION_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

  _PROFILELIST_KEY_VALUE_MAPPINGS = {
      'AllUsersProfile': '%AllUsersProfile%',
      'ProgramData': '%ProgramData%',
      'Public': '%Public%'}

  _WINDOWS_KEY_VALUE_MAPPINGS = {
      'CommonFilesDir': '%CommonProgramFiles%',
      'CommonFilesDir (x86)': '%CommonProgramFiles(x86)%',
      'CommonW6432Dir': '%CommonProgramW6432%',
      'ProgramFilesDir': '%ProgramFiles%',
      'ProgramFilesDir (x86)': '%ProgramFiles(x86)%',
      'ProgramW6432Dir': '%ProgramW6432%'}

  _WINDOWS_NT_KEY_VALUE_MAPPINGS = {
      'SystemRoot': '%SystemRoot%'}

  def _CollectEnvironmentVariablesFromEnvironmentKey(self, registry_key):
    """Collects environment variables.

    Args:
      registry_key (dfwinreg.WinRegistryKey): environment Windows Registry
          key.

    Yields:
      EnvironmentVariable: an environment variable.
    """
    for registry_value in registry_key.GetValues():
      environment_variable_name = '%{0:s}%'.format(registry_value.name)
      value_string = registry_value.GetDataAsObject()
      yield EnvironmentVariable(environment_variable_name, value_string)

  def _CollectEnvironmentVariablesWithMappings(self, registry_key, mappings):
    """Collects environment variables.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Yields:
      EnvironmentVariable: an environment variable.
    """
    for value_name, environment_variable_name in mappings.items():
      registry_value = registry_key.GetValueByName(value_name)
      if registry_value:
        value_string = registry_value.GetDataAsObject()
        yield EnvironmentVariable(environment_variable_name, value_string)

  def Collect(self, registry):
    """Collects environment variables.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      EnvironmentVariable: an environment variable.
    """
    registry_key = registry.GetKeyByPath(self._ENVIRONMENT_KEY_PATH)
    if registry_key:
      yield from self._CollectEnvironmentVariablesFromEnvironmentKey(
          registry_key)

    registry_key = registry.GetKeyByPath(self._PROFILELIST_KEY_PATH)
    if registry_key:
      yield from self._CollectEnvironmentVariablesWithMappings(
          registry_key, self._PROFILELIST_KEY_VALUE_MAPPINGS)

    registry_key = registry.GetKeyByPath(self._WINDOWS_CURRENTVERSION_KEY_PATH)
    if registry_key:
      yield from self._CollectEnvironmentVariablesWithMappings(
          registry_key, self._WINDOWS_KEY_VALUE_MAPPINGS)

    registry_key = registry.GetKeyByPath(
        self._WINDOWS_NT_CURRENTVERSION_KEY_PATH)
    if registry_key:
      yield from self._CollectEnvironmentVariablesWithMappings(
          registry_key, self._WINDOWS_NT_KEY_VALUE_MAPPINGS)
