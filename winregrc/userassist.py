# -*- coding: utf-8 -*-
"""Windows User Assist information collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfwinreg import registry

from winregrc import collector
from winregrc import hexdump
from winregrc import interface


# pylint: disable=logging-format-interpolation

class UserAssistDataParser(object):
  """Class that parses User Assist data."""

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

  def __init__(self, debug=False, output_writer=None):
    """Initializes a parser object.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (OutputWriter): output writer.
    """
    super(UserAssistDataParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

  def ParseEntry(self, format_version, entry_data):
    """Parses an entry.

    Args:
      format_version (int): format version.
      entry_data (bytes): entry data.
    """
    if format_version == 3:
      entry_data_size = self._USER_ASSIST_V3_STRUCT.sizeof()
    elif format_version == 5:
      entry_data_size = self._USER_ASSIST_V5_STRUCT.sizeof()

    if entry_data_size != len(entry_data):
      logging.warning((
          u'Version: {0:d} size mismatch (calculated: {1:d}, '
          u'stored: {2:d}).').format(
              format_version, entry_data_size, len(entry_data)))
      return

    if format_version == 3:
      parsed_data = self._USER_ASSIST_V3_STRUCT.parse(entry_data)
    elif format_version == 5:
      parsed_data = self._USER_ASSIST_V5_STRUCT.parse(entry_data)

    if self._debug:
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


class UserAssistCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a Windows User Assist information collector."""

  _USER_ASSIST_KEY = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\UserAssist')

  # TODO: replace print by output_writer.
  def _CollectUserAssistFromKey(self, unused_output_writer, guid_sub_key):
    """Collects the User Assist information from a GUID sub key.

    Args:
      output_writer (OutputWriter): output writer.
      guid_sub_key (dfwinreg.WinRegistryKey): User Assist GUID Registry key.
    """
    version_value = guid_sub_key.GetValueByName(u'Version')
    if not version_value:
      logging.warning(u'Missing Version value in sub key: {0:s}'.format(
          guid_sub_key.name))
      return

    format_version = version_value.GetDataAsObject()

    if self._debug:
      print(u'GUID\t\t: {0:s}'.format(guid_sub_key.name))
      print(u'Format version\t: {0:d}'.format(format_version))
      print(u'')

    count_sub_key = guid_sub_key.GetSubkeyByName(u'Count')
    for value in count_sub_key.GetValues():
      output_string = u'Original name\t: {0:s}'.format(value.name)

      if self._debug:
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

        if self._debug:
          print(output_string.encode(u'utf-8'))
      except UnicodeEncodeError as exception:
        logging.warning(u'Unable to convert: {0:s} with error: {1:s}'.format(
            value.name, exception))

      if self._debug:
        print(u'Value data:')
        print(hexdump.Hexdump(value.data))

      if value_name != u'UEME_CTLSESSION':
        parser = UserAssistDataParser(debug=self._debug)
        parser.ParseEntry(format_version, value.data)

  def Collect(self, registry, output_writer):
    """Collects the User Assist information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the User Assist key was found, False if not.
    """
    user_assist_key = registry.GetKeyByPath(self._USER_ASSIST_KEY)
    if not user_assist_key:
      return False

    if self._debug:
      print(u'Key: {0:s}'.format(self._USER_ASSIST_KEY))
      print(u'')

    for guid_sub_key in user_assist_key.GetSubkeys():
      self._CollectUserAssistFromKey(output_writer, guid_sub_key)

    return True
