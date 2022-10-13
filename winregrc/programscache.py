# -*- coding: utf-8 -*-
"""Windows Programs Cache information collector."""

import logging
import uuid

from dtfabric.runtime import data_maps as dtfabric_data_maps

import pyfwsi

from winregrc import data_format
from winregrc import errors
from winregrc import interface


class ProgramsCacheDataParser(data_format.BinaryDataFormat):
  """Programs Cache data parser."""

  _DEFINITION_FILE = 'programscache.yaml'

  def _DebugPrintEntryFooter(self, entry_footer):
    """Prints entry footer value debug information.

    Args:
      entry_footer (programscache_entry_footer): entry footer.
    """
    self._DebugPrintValue('Sentinel', f'0x{entry_footer.sentinel:02x}')

  def _DebugPrintEntryHeader(self, entry_header):
    """Prints entry header value debug information.

    Args:
      entry_header (programscache_entry_header): entry header.
    """
    self._DebugPrintDecimalValue('Entry data size', entry_header.data_size)

  def _DebugPrintHeader(self, header):
    """Prints header value debug information.

    Args:
      header (programscache_header): header.
    """
    self._DebugPrintDecimalValue('Format version', header.format_version)

  def _DebugPrintShellItem(self, shell_item):
    """Prints shell item value debug information.

    Args:
      shell_item (pyfwsi.shell_item): shell item.
    """
    self._DebugPrintValue(
        'Shell item class type', f'0x{shell_item.class_type:02x}')

    value_string = getattr(shell_item, 'name', '')
    self._DebugPrintValue('Shell item name', value_string)

  def _ParseEntryFooter(self, value_data, value_data_offset):
    """Parses an entry footer from the value data.

    Args:
      value_data (bytes): value data.
      value_data_offset (int): offset of the entry footer relative to the start
          of the value data.

    Returns:
      tuple: containing:

        programscache_entry_footer: entry footer.
        int: entry footer data size.

    Raises:
      ParseError: if the entry footer could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('programscache_entry_footer')
    data_size = data_type_map.GetSizeHint()

    if self._debug:
      self._DebugPrintData(
          'Entry footer data',
          value_data[value_data_offset:value_data_offset + data_size])

    try:
      entry_footer = self._ReadStructureFromByteStream(
          value_data[value_data_offset:], value_data_offset, data_type_map,
          'entry footer')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          f'Unable to parse entry footer value with error: {exception!s}')

    if self._debug:
      self._DebugPrintEntryFooter(entry_footer)

    return entry_footer, data_size

  def _ParseHeader(self, value_data):
    """Parses a header from the value data.

    Args:
      value_data (bytes): value data.

    Returns:
      tuple: containing:

        programscache_header: header.
        int: header data size.

    Raises:
      ParseError: if the header could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('programscache_header')
    data_size = data_type_map.GetSizeHint()

    if self._debug:
      self._DebugPrintData('Header data', value_data[:data_size])

    try:
      header = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          f'Unable to parse header value with error: {exception!s}')

    if self._debug:
      self._DebugPrintHeader(header)

    if header.format_version not in (1, 9, 12, 19):
      raise errors.ParseError('Unsupported format.')

    return header, data_size

  def Parse(self, value_data):
    """Parses the value data.

    Args:
      value_data (bytes): value data.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if self._debug:
      self._DebugPrintData('Value data', value_data)

    header, value_data_offset = self._ParseHeader(value_data)

    if header.format_version == 1:
      value_data_offset += 4

    elif header.format_version == 9:
      data_type_map = self._GetDataTypeMap('programscache_header9')
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        header9 = self._ReadStructureFromByteStream(
            value_data[value_data_offset:], value_data_offset, data_type_map,
            'header9', context=context)
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError(
            f'Unable to parse header9 value with error: {exception!s}')

      value_data_offset += context.byte_size

      if self._debug:
        self._DebugPrintValue('Unknown1', f'0x{header9.unknown1:08x}')

    elif header.format_version in (12, 19):
      uuid_object = uuid.UUID(bytes_le=value_data[4:20])
      value_data_offset += 16

      if self._debug:
        self._DebugPrintValue('Known folder identifier', f'{uuid_object!s}')

    sentinel = 0
    if header.format_version != 9:
      entry_footer, data_size = self._ParseEntryFooter(
          value_data, value_data_offset)

      value_data_offset += data_size

      sentinel = entry_footer.sentinel

    if self._debug:
      self._DebugPrintText('\n')

    value_data_size = len(value_data)
    while sentinel in (0, 1):
      if value_data_offset >= value_data_size:
        break

      data_type_map = self._GetDataTypeMap('programscache_entry_header')
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        entry_header = self._ReadStructureFromByteStream(
            value_data[value_data_offset:], value_data_offset, data_type_map,
            'entry header', context=context)
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError(
            f'Unable to parse entry header value with error: {exception!s}')

      if self._debug:
        self._DebugPrintValue('Entry data offset', f'0x{value_data_offset:08x}')

        self._DebugPrintEntryHeader(entry_header)

      value_data_offset += context.byte_size

      entry_data_size = entry_header.data_size

      shell_item_list = pyfwsi.item_list()
      shell_item_list.copy_from_byte_stream(value_data[value_data_offset:])

      for shell_item in iter(shell_item_list.items):
        if self._debug:
          self._DebugPrintShellItem(shell_item)

      value_data_offset += entry_data_size

      entry_footer, data_size = self._ParseEntryFooter(
          value_data, value_data_offset)

      value_data_offset += data_size

      if self._debug:
        self._DebugPrintText('\n')

      if entry_footer.sentinel == 2 and value_data_offset < value_data_size:
        # TODO: determine the logic to this value.
        while ord(value_data[value_data_offset]) != 0x00:
          value_data_offset += 1
        value_data_offset += 7

        entry_footer, data_size = self._ParseEntryFooter(
            value_data, value_data_offset)

        value_data_offset += data_size

        if self._debug:
          self._DebugPrintText('\n')

    if value_data_offset < value_data_size:
      self._DebugPrintValue(
          'Trailing data offset', f'0x{value_data_offset:08x}')

      self._DebugPrintData(
          'Trailing data:', value_data[value_data_offset:])


class ProgramsCacheCollector(interface.WindowsRegistryKeyCollector):
  """Windows program cache collector."""

  _STARTPAGE_KEY_PATH = (
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\StartPage')

  _STARTPAGE2_KEY_PATH = (
      'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      'Explorer\\StartPage2')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows program cache collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(ProgramsCacheCollector, self).__init__(debug=debug)
    self._parser = ProgramsCacheDataParser(
        debug=debug, output_writer=output_writer)

  def _CollectProgramsCacheFromValue(self, registry, key_path, value_name):
    """Collects Programs Cache from a Windows Registry value.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
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
      logging.warning(f'Missing {value_name:s} value in key: {key_path:s}')
      return True

    self._parser.Parse(value.data)

    return True

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects the Programs Cache information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the Programs Cache information key was found, False if not.
    """
    result = False

    if self._CollectProgramsCacheFromValue(
        registry, self._STARTPAGE_KEY_PATH, 'ProgramsCache'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, self._STARTPAGE2_KEY_PATH, 'ProgramsCache'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, self._STARTPAGE2_KEY_PATH, 'ProgramsCacheSMP'):
      result = True

    if self._CollectProgramsCacheFromValue(
        registry, self._STARTPAGE2_KEY_PATH, 'ProgramsCacheTBP'):
      result = True

    return result
