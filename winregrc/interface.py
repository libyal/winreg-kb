# -*- coding: utf-8 -*-
"""Classes to implement a Windows Registry key and value collector."""

import abc


class WindowsRegistryKeyCollector(object):
  """Windows Registry key and value collector."""

  def __init__(self, debug=False):
    """Initializes a Windows Registry key and value collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
    """
    super(WindowsRegistryKeyCollector, self).__init__()
    self._debug = debug

  def _GetValueAsStringFromKey(
      self, registry_key, value_name, default_value=u''):
    """Retrieves a value as a string from the Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not registry_key:
      return default_value

    value = registry_key.GetValueByName(value_name)
    if not value:
      return default_value

    return value.GetDataAsObject()

  @abc.abstractmethod
  def Collect(self, registry, output_writer):
    """Collects the Windows Registry keys and values.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the key was found, False if not.
    """
