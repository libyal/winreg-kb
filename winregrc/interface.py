# -*- coding: utf-8 -*-
"""Windows Registry key and value collector."""


class WindowsRegistryKeyCollector(object):
  """Windows Registry key and value collector."""

  def __init__(self, debug=False):
    """Initializes a Windows Registry key and value collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
    """
    super(WindowsRegistryKeyCollector, self).__init__()
    self._debug = debug

  def _GetStringValueFromKey(
      self, registry_key, value_name, default_value=None):
    """Retrieves a string value from a Registry value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not registry_key:
      return default_value

    registry_value = registry_key.GetValueByName(value_name)
    if not registry_value:
      return default_value

    if not registry_value.DataIsString():
      return default_value

    return registry_value.GetDataAsObject()

  def _GetValueDataFromKey(self, registry_key, value_name):
    """Retrieves the value data from a Registry value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.

    Returns:
      bytes: value data or None if not available.
    """
    if not registry_key:
      return None

    registry_value = registry_key.GetValueByName(value_name)
    if not registry_value:
      return None

    return registry_value.data

  def _GetValueFromKey(self, registry_key, value_name, default_value=None):
    """Retrieves a value from a Registry value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not registry_key:
      return default_value

    registry_value = registry_key.GetValueByName(value_name)
    if not registry_value:
      return default_value

    return registry_value.GetDataAsObject()
