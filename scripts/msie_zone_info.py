#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract MSIE zone information."""

import argparse
import logging
import sys

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import msie_zone_info
from winregrc import output_writers
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  _DEFAULT_ZONE_NAMES = {
      '0': 'My Computer',
      '1': 'Local Intranet',
      '2': 'Trusted sites',
      '3': 'Internet',
      '4': 'Restricted sites'}

  # Sources:
  # http://support.microsoft.com/kb/182569
  # http://technet.microsoft.com/en-us/library/cc783259(v=ws.10).aspx
  _CONTROL_DESCRIPTIONS = {
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
      '2101': ('Web sites in less privileged web content zone can navigate '
               'into this zone'),
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
      '2600': 'Enable .NET Framework setup'}

  _CONTROL_VALUES_COMMON_ENABLE = {
      0x00000000: 'Enable',
      0x00000001: 'Prompt',
      0x00000003: 'Disable',
      0x00010000: 'Administrator approved'}

  _CONTROL_VALUES_COMMON_SAFETY = {
      0x00010000: 'High safety',
      0x00020000: 'Medium safety',
      0x00030000: 'Low safety'}

  _CONTROL_VALUES_1A00 = {
      0x00000000: 'Automatic logon with current user name and password',
      0x00010000: 'Prompt for user name and password',
      0x00020000: 'Automatic logon only in Intranet zone',
      0x00030000: 'Anonymous logon'}

  _CONTROL_VALUES_1C00 = {
      0x00000000: 'Disable Java',
      0x00010000: 'High safety',
      0x00020000: 'Medium safety',
      0x00030000: 'Low safety',
      0x00800000: 'Custom'}

  def _GetControlValueDescription(self, control, control_value):
    """Retrieves the description of a specific control value.

    Args:
      control (str): control.
      control_value (str): value to which the control is set.

    Returns:
      str: description of the control value or None if not available.
    """
    if control in (
        '1001', '1004', '1200', '1201', '1400', '1402', '1405', '1406', '1407',
        '1601', '1604', '1606', '1607', '1608', '1609', '1800', '1802', '1803',
        '1804', '1809', '1A04', '2000', '2001', '2004', '2100', '2101', '2102',
        '2200', '2201', '2300'):
      return self._CONTROL_VALUES_COMMON_ENABLE.get(control_value, None)

    if control == '1A00':
      return self._CONTROL_VALUES_1A00.get(control_value, None)

    if control == '1C00':
      return self._CONTROL_VALUES_1C00.get(control_value, None)

    if control == '1E05':
      return self._CONTROL_VALUES_COMMON_SAFETY.get(control_value, None)

    return None

  def WriteZoneInformation(self, zone_information):
    """Writes MSIE zone information to the output.

    Args:
      zone_information (MSIEZoneInformation): MSIE zone information.
    """
    zone_name = zone_information.zone_name
    if not zone_name:
      zone_name = self._DEFAULT_ZONE_NAMES.get(zone_information.zone, None)

    if zone_name:
      text = f'Zone\t\t\t: {zone_information.zone:s} ({zone_name:s})\n'
    else:
      text = f'Zone\t\t\t: {zone_information.zone:s}\n'
    self.WriteText(text)

    control_description = self._CONTROL_DESCRIPTIONS.get(
        zone_information.control, None)

    if control_description:
      text = (f'Control\t\t\t: {zone_information.control:s} '
              f'({control_description:s})\n')
    else:
      text = f'Control\t\t\t: {zone_information.control:s}\n'
    self.WriteText(text)

    control_value_description = self._GetControlValueDescription(
        zone_information.control, zone_information.control_value)

    if control_value_description:
      text = (f'Value\t\t\t: {zone_information.control_value!s} '
              f'({control_value_description:s})\n')
    else:
      text = f'Value\t\t\t: {zone_information.control_value!s}\n'
    self.WriteText(text)

    self.WriteText('\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the MSIE zone information from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a NTUSER.DAT or SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  if not scanner.ScanForWindowsVolume(
      options.source, options=volume_scanner_options):
    print((f'Unable to retrieve the volume with the Windows directory from: '
           f'{options.source:s}.'))
    print('')
    return False

  collector_object = msie_zone_info.MSIEZoneInformationCollector(
      debug=options.debug)

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    has_results = False
    for zone_information in collector_object.Collect(scanner.registry):
      output_writer_object.WriteZoneInformation(zone_information)
      has_results = True

  finally:
    output_writer_object.Close()

  if not has_results:
    print('No MSIE zone information found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
