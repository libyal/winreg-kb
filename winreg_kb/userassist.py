# -*- coding: utf-8 -*-
"""Windows User Assist information collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfwinreg import registry

from winreg_kb import collector
from winreg_kb import hexdump


# pylint: disable=logging-format-interpolation

class UserAssistCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows User Assist information collector."""

  _USER_ASSIST_KEY = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\UserAssist')

  # UserAssist format version used in Windows 2000, XP, 2003, Vista.
  _USER_ASSIST_V3_STRUCT = construct.Struct(
      u'user_assist_entry',
      construct.ULInt32(u'unknown1'),
      construct.ULInt32(u'execution_count'),
      construct.ULInt64(u'last_execution_time'))

  # UserAssist format version used in Windows 2008, 7, 8.
  _USER_ASSIST_V5_STRUCT = construct.Struct(
      u'user_assist_entry',
      construct.ULInt32(u'unknown1'),
      construct.ULInt32(u'execution_count'),
      construct.ULInt32(u'application_focus_count'),
      construct.ULInt32(u'application_focus_duration'),
      construct.LFloat32(u'unknown2'),
      construct.LFloat32(u'unknown3'),
      construct.LFloat32(u'unknown4'),
      construct.LFloat32(u'unknown5'),
      construct.LFloat32(u'unknown6'),
      construct.LFloat32(u'unknown7'),
      construct.LFloat32(u'unknown8'),
      construct.LFloat32(u'unknown9'),
      construct.LFloat32(u'unknown10'),
      construct.LFloat32(u'unknown11'),
      construct.ULInt32(u'unknown12'),
      construct.ULInt64(u'last_execution_time'),
      construct.ULInt32(u'unknown13'))

  def __init__(self, debug=False):
    """Initializes the collector object.

    Args:
      debug: optional boolean value to indicate if debug information should
             be printed.
    """
    super(UserAssistCollector, self).__init__()
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.found_user_assist_key = False

   # TODO: replace print by output_writer.
  def _CollectUserAssistFromKey(self, unused_output_writer, guid_sub_key):
    """Collects the User Assist information from a GUID sub key.

    Args:
      output_writer: the output writer object.
      guid_sub_key: the User Assist GUID key (instance of pyregf.key).
    """
    version_value = guid_sub_key.GetValueByName(u'Version')
    if not version_value:
      logging.warning(u'Missing Version value in sub key: {0:s}'.format(
          guid_sub_key.name))
      return

    format_version = version_value.GetDataAsObject()
    if format_version == 3:
      value_data_size = self._USER_ASSIST_V3_STRUCT.sizeof()
    elif format_version == 5:
      value_data_size = self._USER_ASSIST_V5_STRUCT.sizeof()

    print(u'GUID\t\t: {0:s}'.format(guid_sub_key.name))
    print(u'Format version\t: {0:d}'.format(format_version))
    print(u'')

    count_sub_key = guid_sub_key.GetSubkeyByName(u'Count')
    for value in count_sub_key.GetValues():
      output_string = u'Original name\t: {0:s}'.format(value.name)
      print(output_string.encode(u'utf-8'))

      try:
        value_name = value.name.decode(u'rot-13')
      except UnicodeEncodeError as exception:
        characters = []
        for char in value.name:
          if ord(char) < 128:
            try:
              characters.append(char.decode(u'rot-13'))
            except UnicodeEncodeError:
              characters.append(char)
          else:
            characters.append(char)

        value_name = u''.join(characters)

      try:
        output_string = u'Converted name\t: {0:s}'.format(value_name)
        print(output_string.encode(u'utf-8'))
      except UnicodeEncodeError as exception:
        logging.warning(u'Unable to convert: {0:s} with error: {1:s}'.format(
            value.name, exception))

      print(u'Value data:')
      print(hexdump.Hexdump(value.data))

      if value_name != u'UEME_CTLSESSION':
        if value_data_size != len(value.data):
          logging.warning((
              u'Version: {0:d} size mismatch (calculated: {1:d}, '
              u'stored: {2:d}).').format(
                  format_version, value_data_size, len(value.data)))
          return

        if format_version == 3:
          parsed_data = self._USER_ASSIST_V3_STRUCT.parse(value.data)
        elif format_version == 5:
          parsed_data = self._USER_ASSIST_V5_STRUCT.parse(value.data)

        print(u'Unknown1\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            parsed_data.get(u'unknown1')))

        print(u'Execution count\t\t\t\t\t\t\t\t: {0:d}'.format(
            parsed_data.get(u'execution_count')))

        if format_version == 5:
          print(u'Application focus count\t\t\t\t\t\t\t: {0:d}'.format(
              parsed_data.get(u'application_focus_count')))

          print(u'Application focus duration\t\t\t\t\t\t: {0:d}'.format(
              parsed_data.get(u'application_focus_duration')))

          print(u'Unknown2\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown2')))

          print(u'Unknown3\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown3')))

          print(u'Unknown4\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown4')))

          print(u'Unknown5\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown5')))

          print(u'Unknown6\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown6')))

          print(u'Unknown7\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown7')))

          print(u'Unknown8\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown8')))

          print(u'Unknown9\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown9')))

          print(u'Unknown10\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown10')))

          print(u'Unknown11\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get(u'unknown11')))

          print(u'Unknown12\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
              parsed_data.get(u'unknown12')))

        timestamp = parsed_data.get(u'last_execution_time')
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp/10))

        print(u'Last execution time\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
            date_string, timestamp))

        if format_version == 5:
          print(u'Unknown13\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
              parsed_data.get(u'unknown13')))

        print(u'')

  def Collect(self, output_writer):
    """Collects the User Assist information.

    Args:
      output_writer: the output writer object.
    """
    self.found_user_assist_key = False

    user_assist_key = self._registry.GetKeyByPath(self._USER_ASSIST_KEY)
    if not user_assist_key:
      return

    self.found_user_assist_key = True

    print(u'Key: {0:s}'.format(self._USER_ASSIST_KEY))
    print(u'')

    for guid_sub_key in user_assist_key.GetSubkeys():
      self._CollectUserAssistFromKey(output_writer, guid_sub_key)
