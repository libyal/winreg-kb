# -*- coding: utf-8 -*-
"""Windows Programs Cache information collector."""

from __future__ import print_function
import logging
import uuid

import pyfwsi

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from winregrc import errors
from winregrc import interface


class ProgramsCacheDataParser(object):
  """Programs Cache data parser."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: uint8',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 1',
      b'  units: bytes',
      b'---',
      b'name: uint16',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: programscache_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: format_version',
      b'  data_type: uint32',
      b'---',
      b'name: programscache_header9',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: unknown1',
      b'  data_type: uint16',
      b'---',
      b'name: programscache_entry_header',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: data_size',
      b'  data_type: uint32',
      b'---',
      b'name: programscache_entry_footer',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: sentinel',
      b'  data_type: uint8'])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'programscache_header')

  _HEADER_SIZE = _HEADER.GetByteSize()

  _HEADER9 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'programscache_header9')

  _HEADER9_SIZE = _HEADER9.GetByteSize()

  _ENTRY_HEADER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'programscache_entry_header')

  _ENTRY_HEADER_SIZE = _ENTRY_HEADER.GetByteSize()

  _ENTRY_FOOTER = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'programscache_entry_footer')

  _ENTRY_FOOTER_SIZE = _ENTRY_FOOTER.GetByteSize()

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Programs Cache data parser.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ProgramsCacheDataParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

  def Parse(self, value_data):
    """Parses the value data.

    Args:
      value_data (bytes): value data.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    value_data_size = len(value_data)

    if self._debug:
      self._output_writer.WriteDebugData(u'Value data:', value_data)

    try:
      header = self._HEADER.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    value_data_offset = self._HEADER_SIZE

    if self._debug:
      self._output_writer.WriteIntegerValueAsDecimal(
          u'Format version', header.format_version)

    if header.format_version not in (1, 9, 12, 19):
      raise errors.ParseError(u'Unsupported format.')

    if header.format_version == 1:
      value_data_offset += 4

    elif header.format_version == 9:
      try:
        header9 = self._HEADER9.MapByteStream(value_data)
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      value_data_offset += self._HEADER9_SIZE

      if self._debug:
        value_string = u'0x{0:08x}'.format(header9.unknown2)
        self._output_writer.WriteValue(u'Unknown2', value_string)

    elif header.format_version in (12, 19):
      uuid_object = uuid.UUID(bytes_le=value_data[4:20])
      value_data_offset += 16

      if self._debug:
        value_string = u'{0!s}'.format(uuid_object)
        self._output_writer.WriteValue(u'Known folder identifier', value_string)

    sentinel = 0
    if header.format_version != 9:
      try:
        entry_footer = self._ENTRY_FOOTER.MapByteStream(
            value_data[value_data_offset:])
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      value_data_offset += self._ENTRY_FOOTER_SIZE

      sentinel = entry_footer.sentinel

      if self._debug:
        value_string = u'0x{0:02x}'.format(sentinel)
        self._output_writer.WriteValue(u'Sentinel', value_string)

    if self._debug:
      self._output_writer.WriteText(u'')

    while sentinel in (0, 1):
      try:
        entry_header = self._ENTRY_HEADER.MapByteStream(
            value_data[value_data_offset:])
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      value_data_offset += self._ENTRY_HEADER

      entry_data_size = entry_header.data_size

      if self._debug:
        value_string = u'0x{0:08x}'.format(value_data_offset)
        self._output_writer.WriteValue(u'Entry data offset', value_string)

        self._output_writer.WriteIntegerValueAsDecimal(
            u'Entry data size', entry_data_size)

      shell_item_list = pyfwsi.item_list()
      shell_item_list.copy_from_byte_stream(value_data[value_data_offset:])

      for shell_item in iter(shell_item_list.items):
        if self._debug:
          print(u'Shell item: 0x{0:02x}'.format(shell_item.class_type))
          print(u'Shell item: {0:s}'.format(getattr(shell_item, u'name', u'')))

      value_data_offset += entry_data_size

      try:
        entry_footer = self._ENTRY_FOOTER.MapByteStream(
            value_data[value_data_offset:])
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      value_data_offset += self._ENTRY_FOOTER_SIZE

      if self._debug:
        value_string = u'0x{0:02x}'.format(entry_footer.sentinel)
        self._output_writer.WriteValue(u'Sentinel', value_string)
        self._output_writer.WriteText(u'')

      if entry_footer.sentinel == 2 and value_data_offset < value_data_size:
        # TODO: determine the logic to this value.
        while ord(value_data[value_data_offset]) != 0x00:
          value_data_offset += 1
        value_data_offset += 7

        try:
          entry_footer = self._ENTRY_FOOTER.MapByteStream(
              value_data[value_data_offset:])
        except (
            dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError) as exception:
          raise errors.ParseError(exception)

        value_data_offset += self._ENTRY_FOOTER_SIZE

        if self._debug:
          value_string = u'0x{0:02x}'.format(entry_footer.sentinel)
          self._output_writer.WriteValue(u'Sentinel', value_string)
          self._output_writer.WriteText(u'')

    if value_data_offset < value_data_size:
      value_string = u'0x{0:08x}'.format(value_data_offset)
      self._output_writer.WriteValue(u'Trailing data offset', value_string)

      self._output_writer.WriteDebugData(
          u'Trailing data:', value_data[value_data_offset:])


class ProgramsCacheCollector(interface.WindowsRegistryKeyCollector):
  """Windows program cache collector."""

  _STARTPAGE_KEY_PATH = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\StartPage')

  _STARTPAGE2_KEY_PATH = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\StartPage2')

  def _CollectProgramsCacheFromValue(
      self, registry, output_writer, key_path, value_name):
    """Collects Programs Cache from a Windows Registry value.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.
      key_path (str): path of the Programs Cache key.
      value_name (str): name of the Programs Cache value.

    Returns:
      bool: True if the Programs Cache information key was found, False if not.
    """
    startpage_key = registry.GetKeyByPath(key_path)
    if not startpage_key:
      return False

    value = startpage_key.GetValueByName(value_name)
    if not value:
      logging.warning(u'Missing {0:s} value in key: {1:s}'.format(
          value_name, key_path))
      return True

    parser = ProgramsCacheDataParser(
        debug=self._debug, output_writer=output_writer)

    parser.Parse(value.data)

    return True

  def Collect(self, registry, output_writer):
    """Collects the Programs Cache information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Programs Cache information key was found, False if not.
    """
    result = False

    if self._CollectProgramsCacheFromValue(
        registry, output_writer, self._STARTPAGE_KEY_PATH,
        u'ProgramsCache'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, output_writer, self._STARTPAGE2_KEY_PATH,
        u'ProgramsCache'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, output_writer, self._STARTPAGE2_KEY_PATH,
        u'ProgramsCacheSMP'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, output_writer, self._STARTPAGE2_KEY_PATH,
        u'ProgramsCacheTBP'):
      result = True

    return result
