# -*- coding: utf-8 -*-
"""System information collector."""

from winregrc import interface


class SystemInfoCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a system information collector."""

  _CURRENT_VERSION_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

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

  def Collect(self, registry, output_writer):
    """Collects system information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the system information key was found, False if not.
    """
    current_version_key = registry.GetKeyByPath(
        self._CURRENT_VERSION_KEY_PATH)
    if not current_version_key:
      return False

    value_names = [
        u'ProductName',
        u'CSDVersion',
        u'CurrentVersion',
        u'CurrentBuildNumber',
        u'CurrentType',
        u'ProductId',
        u'RegisteredOwner',
        u'RegisteredOrganization',
        u'PathName',
        u'SystemRoot',
    ]

    for value_name in value_names:
      value_string = self._GetValueAsStringFromKey(
          current_version_key, value_name)
      output_writer.WriteText(u'{0:s}: {1:s}'.format(value_name, value_string))

    value = current_version_key.GetValueByName(u'InstallDate')
    if value:
      output_writer.WriteText(
          u'InstallDate: {0:d}'.format(value.GetDataAsObject()))

    return True
