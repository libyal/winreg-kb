# -*- coding: utf-8 -*-
"""Microsoft Internet Explorer (MSIE) zone information collector."""

from __future__ import print_function
from __future__ import unicode_literals

from winregrc import interface


DEFAULT_ZONE_NAMES = {
    '0': 'My Computer',
    '1': 'Local Intranet Zone',
    '2': 'Trusted sites Zone',
    '3': 'Internet Zone',
    '4': 'Restricted Sites Zone',
}

# Sources:
# http://support.microsoft.com/kb/182569
# http://technet.microsoft.com/en-us/library/cc783259(v=ws.10).aspx
CONTROL_DESCRIPTIONS = {
    '1001': 'Download signed ActiveX controls',
    '1004': 'Download unsigned ActiveX controls',
    '1200': 'Run ActiveX controls and plug-ins',
    '1201': ('Initialize and script ActiveX controls not marked as safe for '
             'scripting'),
    '1206': 'Allow scripting of Internet Explorer Web browser control',
    '1207': 'Reserved',
    '1208': 'Allow previously unused ActiveX controls to run without prompt',
    '1209': 'Allow Scriptlets',
    '120A': 'Override Per-Site (domain-based) ActiveX restrictions',
    '120B': 'Override Per-Site (domain-based) ActiveX restrictions',
    '1400': 'Active scripting',
    '1402': 'Scripting of Java applets',
    '1405': 'Script ActiveX controls marked as safe for scripting',
    '1406': 'Access data sources across domains',
    '1407': 'Allow Programmatic clipboard access',
    '1408': 'Reserved',
    '1601': 'Submit non-encrypted form data',
    '1604': 'Font download',
    '1605': 'Run Java',
    '1606': 'Userdata persistence',
    '1607': 'Navigate sub-frames across different domains',
    '1608': 'Allow META REFRESH',
    '1609': 'Display mixed content',
    '160A': 'Include local directory path when uploading files to a server',
    '1800': 'Installation of desktop items',
    '1802': 'Drag and drop or copy and paste files',
    '1803': 'File Download',
    '1804': 'Launching programs and files in an IFRAME',
    '1805': 'Launching programs and files in webview',
    '1806': 'Launching applications and unsafe files',
    '1807': 'Reserved',
    '1808': 'Reserved',
    '1809': 'Use Pop-up Blocker',
    '180A': 'Reserved',
    '180B': 'Reserved',
    '180C': 'Reserved',
    '180D': 'Reserved',
    '1A00': 'Logon',
    '1A02': 'Allow persistent cookies that are stored on your computer',
    '1A03': 'Allow per-session cookies (not stored)',
    '1A04': ('Don\'t prompt for client certificate selection when no '
             'certificates or only one certificate exists'),
    '1A05': 'Allow 3rd party persistent cookies',
    '1A06': 'Allow 3rd party session cookies',
    '1A10': 'Privacy Settings',
    '1C00': 'Java permissions',
    '1E05': 'Software channel permissions',
    '1F00': 'Reserved',
    '2000': 'Binary and script behaviors',
    '2001': 'Run components signed with Authenticode',
    '2004': 'Run components not signed with Authenticode',
    '2100': 'Open files based on content, not file extension',
    '2101': ('Web sites in less privileged web content zone can navigate into '
             'this zone'),
    '2102': ('Allow script initiated windows without size or position '
             'constraints'),
    '2103': 'Allow status bar updates via script',
    '2104': 'Allow websites to open windows without address or status bars',
    '2105': 'Allow websites to prompt for information using scripted windows',
    '2200': 'Automatic prompting for file downloads',
    '2201': 'Automatic prompting for ActiveX controls',
    '2300': 'Allow web pages to use restricted protocols for active content',
    '2301': 'Use Phishing Filter',
    '2400': '.NET Framework: XAML browser applications',
    '2401': '.NET Framework: XPS documents',
    '2402': '.NET Framework: Loose XAML',
    '2500': 'Turn on Protected Mode [Vista only setting]',
    '2600': 'Enable .NET Framework setup',
}

CONTROL_VALUES_COMMON_ENABLE = {
    0x00000000: 'Enable',
    0x00000001: 'Prompt',
    0x00000003: 'Disable',
    0x00010000: 'Administrator approved',
}

CONTROL_VALUES_COMMON_SAFETY = {
    0x00010000: 'High safety',
    0x00020000: 'Medium safety',
    0x00030000: 'Low safety',
}

CONTROL_VALUES_1A00 = {
    0x00000000: 'Automatic logon with current user name and password',
    0x00010000: 'Prompt for user name and password',
    0x00020000: 'Automatic logon only in Intranet zone',
    0x00030000: 'Anonymous logon',
}

CONTROL_VALUES_1C00 = {
    0x00000000: 'Disable Java',
    0x00010000: 'High safety',
    0x00020000: 'Medium safety',
    0x00030000: 'Low safety',
    0x00800000: 'Custom',
}


class MSIEZoneInfoCollector(interface.WindowsRegistryKeyCollector):
  """MSIE zone information collector."""

  def _PrintLockdownKey(self, registry, lockdown_key_path):
    """Prints a lockdown key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      lockdown_key_path (str): lockdown Registry key path.
    """
    lockdown_key = registry.GetKeyByPath(lockdown_key_path)
    if not lockdown_key:
      return

    if self._debug:
      print('Key: {0:s}'.format(lockdown_key_path))
      print('')

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

  def _PrintZonesKey(self, registry, zones_key_path, output_mode=0):
    """Prints a zones key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      zones_key_path (str): zones Registry key path.
      output_mode (Optional[int]): output mode.
    """
    zones_key = registry.GetKeyByPath(zones_key_path)
    if not zones_key:
      return

    if self._debug:
      print('Key: {0:s}'.format(zones_key_path))
      print('')

    for zone_key in zones_key.GetSubkeys():
      # TODO: the zone names are defined in another key.
      if zone_key.name in DEFAULT_ZONE_NAMES:
        if self._debug:
          print('Zone: {0:s}: {1:s}'.format(
              zone_key.name, DEFAULT_ZONE_NAMES[zone_key.name]))
      else:
        if self._debug:
          print('Zone: {0:s}'.format(zone_key.name))

      for setting_value in zone_key.GetValues():
        if not setting_value.name:
          continue

        if setting_value.name in [
            'Description', 'DisplayName', 'PMDisplayName']:
          if output_mode == 0:
            if self._debug:
              print('{0:s}: {1:s}'.format(
                  setting_value.name, setting_value.GetDataAsObject()))

        elif len(setting_value.name) == 4 and setting_value.name != 'Icon':
          if len(setting_value.data) != 4:
            if output_mode == 0:
              if self._debug:
                print('Value: {0:s}'.format(setting_value.data.encode('hex')))

          else:
            value = setting_value.GetDataAsObject()
            value_desc = ''

            if setting_value.name in [
                '1001', '1004', '1200', '1201', '1400', '1402', '1405',
                '1406', '1407', '1601', '1604', '1606', '1607', '1608',
                '1609', '1800', '1802', '1803', '1804', '1809', '1A04',
                '2000', '2001', '2004', '2100', '2101', '2102', '2200',
                '2201', '2300']:
              value_desc = CONTROL_VALUES_COMMON_ENABLE.get(value, '')

            elif setting_value.name == '1A00':
              value_desc = CONTROL_VALUES_1A00.get(value, '')

            elif setting_value.name == '1C00':
              value_desc = CONTROL_VALUES_1C00.get(value, '')

            elif setting_value.name == '1E05':
              value_desc = CONTROL_VALUES_COMMON_SAFETY.get(value, '')

          if output_mode == 0:
            if setting_value.name in CONTROL_DESCRIPTIONS:
              if self._debug:
                print('Control: {0:s}: {1:s}'.format(
                    setting_value.name,
                    CONTROL_DESCRIPTIONS[setting_value.name]))
            else:
              if self._debug:
                print('Control: {0:s}'.format(setting_value.name))
            if value_desc:
              if self._debug:
                print('Data: 0x{0:08x}: {1:s}'.format(value, value_desc))
            else:
              if self._debug:
                print('Data: 0x{0:08x}'.format(value))

          elif output_mode == 1:
            if setting_value.name in CONTROL_DESCRIPTIONS:
              control_desc = CONTROL_DESCRIPTIONS[setting_value.name]
            else:
              control_desc = ''

            if self._debug:
              print('{0:s}\t0x{1:08x}\t{2:s}\t{3:s}'.format(
                  setting_value.name, value, value_desc, control_desc))

        else:
          if output_mode == 0:
            if self._debug:
              print('Value: {0:s}'.format(setting_value.name))

      if self._debug:
        print('')

  def Collect(self, registry, output_writer):
    """Collects the MSIE zone information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the MSIE zone information key was found, False if not.
    """
    result = False

    output_mode = 1

    # TODO: pass output_writer
    _ = output_writer

    # HKEY_CURRENT_USER

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Internet Explorer\\'
        'Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Microsoft\\Internet Explorer\\Main\\'
        'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # HKEY_LOCAL_MACHINE

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\'
        'Internet Explorer\\Main\\FeatureControl\\'
        'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Internet Explorer\\Main\\'
        'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # HKEY_LOCAL_MACHINE WoW64

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        'Internet Explorer\\Main\\FeatureControl\\'
        'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\'
        'Internet Explorer\\Main\\FeatureControl\\'
        'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # TODO: check for value Policies\\Microsoft\\Windows\\CurrentVersion\\
    # Internet Settings\\Security_HKEY_LOCAL_MACHINE_only and its data
    # if not exists or 0, not enabled if 1 only HKLM policy applies

    # HKEY_CURRENT_USER

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    # HKEY_LOCAL_MACHINE

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        'Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    # HKEY_LOCAL_MACHINE WoW64

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        'Windows\\CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        'Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
        'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    return result
