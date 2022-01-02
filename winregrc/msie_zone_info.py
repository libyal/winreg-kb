# -*- coding: utf-8 -*-
"""Microsoft Internet Explorer (MSIE) zone information collector."""

from winregrc import interface


class MSIEZoneInformation(object):
  """MSIE zone information.

  Attributes:
    control (str): control.
    control_value (int|str): value to which the control is set.
    zone (str): identifier of the zone to which the control applies.
    zone_name (str): name of the zone to which the control applies.
  """

  def __init__(self, zone, zone_name, control, control_value):
    """Initializes MSIE zone information.

    Args:
      zone (str): identifier of the zone to which the control applies.
      zone_name (str): name of the zone to which the control applies.
      control (str): control.
      control_value (int|str): value to which the control is set.
    """
    super(MSIEZoneInformation, self).__init__()
    self.control = control
    self.control_value = control_value
    self.zone = zone
    self.zone_name = zone_name


class MSIEZoneInformationCollector(interface.WindowsRegistryKeyCollector):
  """MSIE zone information collector."""

  _LOCKDOWN_KEY_PATHS = [
      # HKEY_CURRENT_USER
      ('HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Internet Explorer\\'
       'Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Internet Explorer\\Main\\'
       'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN'),
      # HKEY_LOCAL_MACHINE
      ('HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\'
       'Internet Explorer\\Main\\FeatureControl\\'
       'FEATURE_LOCALMACHINE_LOCKDOWN'),
      ('HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Internet Explorer\\Main\\'
       'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN'),
      # HKEY_LOCAL_MACHINE WoW64
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
       'Internet Explorer\\Main\\FeatureControl\\'
       'FEATURE_LOCALMACHINE_LOCKDOWN'),
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\'
       'Internet Explorer\\Main\\FeatureControl\\'
       'FEATURE_LOCALMACHINE_LOCKDOWN')]

  _ZONES_KEY_PATHS = [
      # HKEY_CURRENT_USER
      ('HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Zones'),
      ('HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Lockdown_Zones'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Internet Settings\\Zones'),
      ('HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Internet Settings\\Lockdown_Zones'),
      # HKEY_LOCAL_MACHINE
      ('HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Lockdown_Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Internet Settings\\Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
       'Internet Settings\\Lockdown_Zones'),
      # HKEY_LOCAL_MACHINE WoW64
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
       'Windows\\CurrentVersion\\Internet Settings\\Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
       'Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Zones'),
      ('HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
       'CurrentVersion\\Internet Settings\\Lockdown_Zones')]

  def _CollectZoneInformationFromLockdownKey(self, lockdown_key):
    """Collects MSIE zone information from a lockdown key.

    Args:
      lockdown_key (dfwinreg.WinRegistryKey): lockdown Windows Registry key.
    """
    program_name = 'iexplore.exe'
    program_value = lockdown_key.GetValueByName(program_name)

    if program_value:
      value = program_value.GetDataAsObject()
    else:
      value = 0

    if self._debug:
      if value == 1:
        print('Local Machine lockdown for {0:s}: True'.format(program_name))
      else:
        print('Local Machine lockdown for {0:s}: False'.format(program_name))
      print('')

    # TODO: implement.

  def _CollectZoneInformationFromZonesKey(self, zones_key):
    """Collects MSIE zone information from a zones key.

    Args:
      zones_key (dfwinreg.WinRegistryKey): zones Windows Registry key.

    Yields:
      MSIEZoneInformation: MSIE zone information.
    """
    for zone_key in zones_key.GetSubkeys():
      zone_name = self._GetValueFromKey(zone_key, 'DisplayName')

      for setting_value in zone_key.GetValues():
        # The 'Description' value contains a description of the zone.
        # The 'PMDisplayName' value contains the display name of the zone in
        # protected mode.
        if setting_value.name in (
            None, 'Description', 'DisplayName', 'PMDisplayName'):
          continue

        if len(setting_value.name) == 4 and setting_value.name != 'Icon':
          if len(setting_value.data) != 4:
            value_string = setting_value.data.encode('hex')
          else:
            value_string = setting_value.GetDataAsObject()

        else:
          value_string = None

        yield MSIEZoneInformation(
            zone_key.name, zone_name, setting_value.name, value_string)

  def Collect(self, registry):
    """Collects the MSIE zone information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      MSIEZoneInformation: MSIE zone information.
    """
    for key_path in self._LOCKDOWN_KEY_PATHS:
      lockdown_key = registry.GetKeyByPath(key_path)
      if lockdown_key:
        # TODO: do something with information in lockdown key
        self._CollectZoneInformationFromLockdownKey(lockdown_key)

    # TODO: check for value Policies\\Microsoft\\Windows\\CurrentVersion\\
    # Internet Settings\\Security_HKEY_LOCAL_MACHINE_only and its data
    # if not exists or 0, not enabled if 1 only HKLM policy applies

    for key_path in self._ZONES_KEY_PATHS:
      zones_key = registry.GetKeyByPath(key_path)
      if zones_key:
        yield from self._CollectZoneInformationFromZonesKey(zones_key)
