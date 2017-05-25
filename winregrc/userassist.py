# -*- coding: utf-8 -*-
"""Windows User Assist information collector."""

from __future__ import print_function
import datetime
import logging

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from winregrc import errors
from winregrc import interface


class UserAssistDataParser(object):
  """User Assist data parser."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: float32',
      b'type: floating-point',
      b'attributes:',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint64',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: user_assist_entry_v3',
      b'type: structure',
      (b'description: UserAssist format version used in Windows 2000, XP, '
       b'2003, Vista.'),
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: execution_count',
      b'  data_type: uint32',
      b'- name: last_execution_time',
      b'  data_type: uint64',
      b'---',
      b'name: user_assist_entry_v5',
      b'type: structure',
      (b'description: UserAssist format version used in Windows 2008, 7, 8, '
       b'10.'),
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: execution_count',
      b'  data_type: uint32',
      b'- name: application_focus_count',
      b'  data_type: uint32',
      b'- name: application_focus_duration',
      b'  data_type: uint32',
      b'- name: unknown2',
      b'  data_type: float32',
      b'- name: unknown3',
      b'  data_type: float32',
      b'- name: unknown4',
      b'  data_type: float32',
      b'- name: unknown5',
      b'  data_type: float32',
      b'- name: unknown6',
      b'  data_type: float32',
      b'- name: unknown7',
      b'  data_type: float32',
      b'- name: unknown8',
      b'  data_type: float32',
      b'- name: unknown9',
      b'  data_type: float32',
      b'- name: unknown10',
      b'  data_type: float32',
      b'- name: unknown11',
      b'  data_type: float32',
      b'- name: unknown12',
      b'  data_type: uint32',
      b'- name: last_execution_time',
      b'  data_type: uint64',
      b'- name: unknown13',
      b'  data_type: uint32'])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _USER_ASSIST_ENTRY_V3 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'user_assist_entry_v3')

  _USER_ASSIST_ENTRY_V5 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'user_assist_entry_v5')

  def __init__(self, debug=False, output_writer=None):
    """Initializes an User Assist data parser.

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

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if format_version == 3:
      data_type_map = self._USER_ASSIST_ENTRY_V3
    elif format_version == 5:
      data_type_map = self._USER_ASSIST_ENTRY_V5

    entry_data_size = data_type_map.GetByteSize()
    if entry_data_size != len(entry_data):
      logging.warning((
          u'Version: {0:d} size mismatch (calculated: {1:d}, '
          u'stored: {2:d}).').format(
              format_version, entry_data_size, len(entry_data)))
      return

    try:
      user_assist_entry = data_type_map.MapByteStream(entry_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    if self._debug:
      value_string = u'0x{0:08x}'.format(user_assist_entry.unknown1)
      self._output_writer.WriteValue(u'Unknown1', value_string)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Execution count', user_assist_entry.execution_count)

      if format_version == 5:
        self._output_writer.WriteIntegerValueAsDecimal(
            u'Application focus count',
            user_assist_entry.application_focus_count)

        self._output_writer.WriteIntegerValueAsDecimal(
            u'Application focus duration',
            user_assist_entry.application_focus_duration)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown2)
        self._output_writer.WriteValue(u'Unknown2', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown3)
        self._output_writer.WriteValue(u'Unknown3', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown4)
        self._output_writer.WriteValue(u'Unknown4', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown5)
        self._output_writer.WriteValue(u'Unknown5', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown6)
        self._output_writer.WriteValue(u'Unknown6', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown7)
        self._output_writer.WriteValue(u'Unknown7', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown8)
        self._output_writer.WriteValue(u'Unknown8', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown9)
        self._output_writer.WriteValue(u'Unknown9', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown10)
        self._output_writer.WriteValue(u'Unknown10', value_string)

        value_string = u'{0:.2f}'.format(user_assist_entry.unknown11)
        self._output_writer.WriteValue(u'Unknown11', value_string)

        value_string = u'0x{0:08x}'.format(user_assist_entry.unknown12)
        self._output_writer.WriteValue(u'Unknown12', value_string)

      timestamp = user_assist_entry.last_execution_time
      date_string = (datetime.datetime(1601, 1, 1) +
                     datetime.timedelta(microseconds=timestamp/10))

      value_string = u'{0!s} (0x{1:08x})'.format(date_string, timestamp)
      self._output_writer.WriteValue(u'Last execution time', value_string)

      if format_version == 5:
        value_string = u'0x{0:08x}'.format(user_assist_entry.unknown13)
        self._output_writer.WriteValue(u'Unknown13', value_string)

      self._output_writer.WriteText(u'')


class UserAssistCollector(interface.WindowsRegistryKeyCollector):
  """Windows User Assist information collector."""

  _USER_ASSIST_KEY = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\UserAssist')

  # TODO: replace print by output_writer.
  def _CollectUserAssistFromKey(self, output_writer, guid_subkey):
    """Collects the User Assist information from a GUID sub key.

    Args:
      output_writer (OutputWriter): output writer.
      guid_subkey (dfwinreg.WinRegistryKey): User Assist GUID Registry key.
    """
    version_value = guid_subkey.GetValueByName(u'Version')
    if not version_value:
      logging.warning(u'Missing Version value in sub key: {0:s}'.format(
          guid_subkey.name))
      return

    format_version = version_value.GetDataAsObject()

    if self._debug:
      print(u'GUID\t\t: {0:s}'.format(guid_subkey.name))
      print(u'Format version\t: {0:d}'.format(format_version))
      print(u'')

    count_subkey = guid_subkey.GetSubkeyByName(u'Count')
    for value in count_subkey.GetValues():
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
        output_writer.WriteDebugData(u'Value data:', value.data)

      if value_name != u'UEME_CTLSESSION':
        parser = UserAssistDataParser(
            debug=self._debug, output_writer=output_writer)
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

    for guid_subkey in user_assist_key.GetSubkeys():
      self._CollectUserAssistFromKey(output_writer, guid_subkey)

    return True
