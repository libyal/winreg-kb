# -*- coding: utf-8 -*-
"""Microsoft Internet Explorer (MSIE) zone information collector."""

from __future__ import print_function

from winregrc import interface


DEFAULT_ZONE_NAMES = {
    u'0': u'My Computer',
    u'1': u'Local Intranet Zone',
    u'2': u'Trusted sites Zone',
    u'3': u'Internet Zone',
    u'4': u'Restricted Sites Zone',
}

# Sources:
# http://support.microsoft.com/kb/182569
# http://technet.microsoft.com/en-us/library/cc783259(v=ws.10).aspx
CONTROL_DESCRIPTIONS = {
    u'1001': 'Download signed ActiveX controls',
    u'1004': 'Download unsigned ActiveX controls',
    u'1200': 'Run ActiveX controls and plug-ins',
    u'1201': ('Initialize and script ActiveX controls not marked as safe for '
              'scripting'),
    u'1206': 'Allow scripting of Internet Explorer Web browser control',
    u'1207': 'Reserved',
    u'1208': 'Allow previously unused ActiveX controls to run without prompt',
    u'1209': 'Allow Scriptlets',
    u'120A': 'Override Per-Site (domain-based) ActiveX restrictions',
    u'120B': 'Override Per-Site (domain-based) ActiveX restrictions',
    u'1400': 'Active scripting',
    u'1402': 'Scripting of Java applets',
    u'1405': 'Script ActiveX controls marked as safe for scripting',
    u'1406': 'Access data sources across domains',
    u'1407': 'Allow Programmatic clipboard access',
    u'1408': 'Reserved',
    u'1601': 'Submit non-encrypted form data',
    u'1604': 'Font download',
    u'1605': 'Run Java',
    u'1606': 'Userdata persistence',
    u'1607': 'Navigate sub-frames across different domains',
    u'1608': 'Allow META REFRESH',
    u'1609': 'Display mixed content',
    u'160A': 'Include local directory path when uploading files to a server',
    u'1800': 'Installation of desktop items',
    u'1802': 'Drag and drop or copy and paste files',
    u'1803': 'File Download',
    u'1804': 'Launching programs and files in an IFRAME',
    u'1805': 'Launching programs and files in webview',
    u'1806': 'Launching applications and unsafe files',
    u'1807': 'Reserved',
    u'1808': 'Reserved',
    u'1809': 'Use Pop-up Blocker',
    u'180A': 'Reserved',
    u'180B': 'Reserved',
    u'180C': 'Reserved',
    u'180D': 'Reserved',
    u'1A00': 'Logon',
    u'1A02': 'Allow persistent cookies that are stored on your computer',
    u'1A03': 'Allow per-session cookies (not stored)',
    u'1A04': ('Don\'t prompt for client certificate selection when no '
              'certificates or only one certificate exists'),
    u'1A05': 'Allow 3rd party persistent cookies',
    u'1A06': 'Allow 3rd party session cookies',
    u'1A10': 'Privacy Settings',
    u'1C00': 'Java permissions',
    u'1E05': 'Software channel permissions',
    u'1F00': 'Reserved',
    u'2000': 'Binary and script behaviors',
    u'2001': 'Run components signed with Authenticode',
    u'2004': 'Run components not signed with Authenticode',
    u'2100': 'Open files based on content, not file extension',
    u'2101': ('Web sites in less privileged web content zone can navigate into '
              'this zone'),
    u'2102': ('Allow script initiated windows without size or position '
              'constraints'),
    u'2103': 'Allow status bar updates via script',
    u'2104': 'Allow websites to open windows without address or status bars',
    u'2105': 'Allow websites to prompt for information using scripted windows',
    u'2200': 'Automatic prompting for file downloads',
    u'2201': 'Automatic prompting for ActiveX controls',
    u'2300': 'Allow web pages to use restricted protocols for active content',
    u'2301': 'Use Phishing Filter',
    u'2400': '.NET Framework: XAML browser applications',
    u'2401': '.NET Framework: XPS documents',
    u'2402': '.NET Framework: Loose XAML',
    u'2500': 'Turn on Protected Mode [Vista only setting]',
    u'2600': 'Enable .NET Framework setup',
}

CONTROL_VALUES_COMMON_ENABLE = {
    0x00000000: u'Enable',
    0x00000001: u'Prompt',
    0x00000003: u'Disable',
    0x00010000: u'Administrator approved',
}

CONTROL_VALUES_COMMON_SAFETY = {
    0x00010000: u'High safety',
    0x00020000: u'Medium safety',
    0x00030000: u'Low safety',
}

CONTROL_VALUES_1A00 = {
    0x00000000: u'Automatic logon with current user name and password',
    0x00010000: u'Prompt for user name and password',
    0x00020000: u'Automatic logon only in Intranet zone',
    0x00030000: u'Anonymous logon',
}

CONTROL_VALUES_1C00 = {
    0x00000000: u'Disable Java',
    0x00010000: u'High safety',
    0x00020000: u'Medium safety',
    0x00030000: u'Low safety',
    0x00800000: u'Custom',
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
      print(u'Key: {0:s}'.format(lockdown_key_path))
      print(u'')

    program_name = u'iexplore.exe'
    program_value = lockdown_key.GetValueByName(program_name)

    if program_value:
      value = program_value.GetDataAsObject()
    else:
      value = 0

    if self._debug:
      if value == 1:
        print(u'Local Machine lockdown for {0:s}: True'.format(program_name))
      else:
        print(u'Local Machine lockdown for {0:s}: False'.format(program_name))
      print(u'')

  def _PrintZonesKey(self, registry, zones_key_path, output_mode=0):
    """Prints a zones key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      lockdown_key_path (str): zones Registry key path.
      output_mode (Optional[int]): output mode.
    """
    zones_key = registry.GetKeyByPath(zones_key_path)
    if not zones_key:
      return

    if self._debug:
      print(u'Key: {0:s}'.format(zones_key_path))
      print(u'')

    for zone_key in zones_key.GetSubkeys():
      # TODO: the zone names are defined in another key.
      if zone_key.name in DEFAULT_ZONE_NAMES:
        if self._debug:
          print(u'Zone: {0:s}: {1:s}'.format(
              zone_key.name, DEFAULT_ZONE_NAMES[zone_key.name]))
      else:
        if self._debug:
          print(u'Zone: {0:s}'.format(zone_key.name))

      for setting_value in zone_key.GetValues():
        if not setting_value.name:
          continue

        elif setting_value.name in [
            u'Description', u'DisplayName', u'PMDisplayName']:
          if output_mode == 0:
            if self._debug:
              print(u'{0:s}: {1:s}'.format(
                  setting_value.name, setting_value.GetDataAsObject()))

        elif len(setting_value.name) == 4 and setting_value.name != u'Icon':
          if len(setting_value.data) != 4:
            if output_mode == 0:
              if self._debug:
                print(u'Value: {0:s}'.format(setting_value.data.encode(u'hex')))

          else:
            value = setting_value.GetDataAsObject()
            value_desc = u''

            if setting_value.name in [
                u'1001', u'1004', u'1200', u'1201', u'1400', u'1402', u'1405',
                u'1406', u'1407', u'1601', u'1604', u'1606', u'1607', u'1608',
                u'1609', u'1800', u'1802', u'1803', u'1804', u'1809', u'1A04',
                u'2000', u'2001', u'2004', u'2100', u'2101', u'2102', u'2200',
                u'2201', u'2300']:
              if value in CONTROL_VALUES_COMMON_ENABLE:
                value_desc = CONTROL_VALUES_COMMON_ENABLE[value]

            elif setting_value.name == u'1A00':
              if value in CONTROL_VALUES_1A00:
                value_desc = CONTROL_VALUES_1A00[value]

            elif setting_value.name == u'1C00':
              if value in CONTROL_VALUES_1C00:
                value_desc = CONTROL_VALUES_1C00[value]

            elif setting_value.name == u'1E05':
              if value in CONTROL_VALUES_COMMON_SAFETY:
                value_desc = CONTROL_VALUES_COMMON_SAFETY[value]

          if output_mode == 0:
            if setting_value.name in CONTROL_DESCRIPTIONS:
              if self._debug:
                print(u'Control: {0:s}: {1:s}'.format(
                    setting_value.name,
                    CONTROL_DESCRIPTIONS[setting_value.name]))
            else:
              if self._debug:
                print(u'Control: {0:s}'.format(setting_value.name))
            if value_desc:
              if self._debug:
                print(u'Data: 0x{0:08x}: {1:s}'.format(value, value_desc))
            else:
              if self._debug:
                print(u'Data: 0x{0:08x}'.format(value))

          elif output_mode == 1:
            if setting_value.name in CONTROL_DESCRIPTIONS:
              control_desc = CONTROL_DESCRIPTIONS[setting_value.name]
            else:
              control_desc = u''

            if self._debug:
              print(u'{0:s}\t0x{1:08x}\t{2:s}\t{3:s}'.format(
                  setting_value.name, value, value_desc, control_desc))

        else:
          if output_mode == 0:
            if self._debug:
              print(u'Value: {0:s}'.format(setting_value.name))

      if self._debug:
        print(u'')

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
        u'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Internet Explorer\\'
        u'Main\\FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        u'HKEY_CURRENT_USER\\Software\\Microsoft\\Internet Explorer\\Main\\'
        u'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # HKEY_LOCAL_MACHINE

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\'
        u'Internet Explorer\\Main\\FeatureControl\\'
        u'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Internet Explorer\\Main\\'
        u'FeatureControl\\FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # HKEY_LOCAL_MACHINE WoW64

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        u'Internet Explorer\\Main\\FeatureControl\\'
        u'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\'
        u'Internet Explorer\\Main\\FeatureControl\\'
        u'FEATURE_LOCALMACHINE_LOCKDOWN')
    self._PrintLockdownKey(registry, key_path)

    # TODO: check for value Policies\\Microsoft\\Windows\\CurrentVersion\\
    # Internet Settings\\Security_HKEY_LOCAL_MACHINE_only and its data
    # if not exists or 0, not enabled if 1 only HKLM policy applies

    # HKEY_CURRENT_USER

    key_path = (
        u'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        u'Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        u'Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    # HKEY_LOCAL_MACHINE

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        u'Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\'
        u'Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    # HKEY_LOCAL_MACHINE WoW64

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        u'Windows\\CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Policies\\Microsoft\\'
        u'Windows\\CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    key_path = (
        u'HKEY_LOCAL_MACHINE\\Software\\Wow6432Node\\Microsoft\\Windows\\'
        u'CurrentVersion\\Internet Settings\\Lockdown_Zones')
    self._PrintZonesKey(registry, key_path, output_mode=output_mode)

    return result
