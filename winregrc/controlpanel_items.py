# -*- coding: utf-8 -*-
"""Windows control panel items collector."""

from winregrc import interface


class ControlPanelItem(object):
  """Control panel item.

  Attributes:
    identifier (str): identifier.
    module_name (str): module name.
  """

  def __init__(self, identifier, module_name):
    """Initializes a control panel item.

    Args:
      identifier (str): identifier.
      module_name (str): module name.
    """
    super(ControlPanelItem, self).__init__()
    self.identifier = identifier
    self.module_name = module_name


class ControlPanelItemsCollector(interface.WindowsRegistryKeyCollector):
  """Windows control panel items collector."""

  _CONTROL_PANEL_NAMESPACE_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\ControlPanel\\NameSpace')

  def _CollectControlPanelItems(self, control_panel_namespace_key):
    """Collects Windows control panel items.

    Args:
      control_panel_namespace_key (dfwinreg.WinRegistryKey): control panel
          namespace Windows Registry key.

    Yields:
      ControlPanelItem: a control panel item.
    """
    for subkey in control_panel_namespace_key.GetSubkeys():
      if subkey.name[0] == '{' and subkey.name[-1] == '}':
        identifier = subkey.name.lower()
        module_name = self._GetValueFromKey(subkey, '')
        yield ControlPanelItem(identifier, module_name)

  def Collect(self, registry):
    """Collects Windows control panel items.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      ControlPanelItem: a control panel item.
    """
    control_panel_namespace_key = registry.GetKeyByPath(
        self._CONTROL_PANEL_NAMESPACE_KEY_PATH)
    if control_panel_namespace_key:
      yield from self._CollectControlPanelItems(control_panel_namespace_key)
