# -*- coding: utf-8 -*-
"""Application Compatibility Cache collector."""

from __future__ import unicode_literals

import logging

from dtfabric.runtime import data_maps as dtfabric_data_maps

from winregrc import data_format
from winregrc import errors
from winregrc import interface


class AppCompatCacheHeader(object):
  """Application Compatibility Cache header.

  Attributes:
    number_of_cached_entries (int): number of cached entries.
    header_size (int): header size.
  """

  def __init__(self):
    """Initializes an Application Compatibility Cache header."""
    super(AppCompatCacheHeader, self).__init__()
    self.number_of_cached_entries = 0
    self.header_size = 0


class AppCompatCacheCachedEntry(object):
  """Application Compatibility Cache cached entry.

  Attributes:
    cached_entry_size (int): size of the cached entry.
    data (bytes): data of the cached entry.
    file_size (int): size of file corresponding to the cached entry.
    insertion_flags (int): insertion flags of the cached entry.
    last_modification_time (int): last modification timestamp of the file
        corresponding to the cached entry.
    last_update_time (int): last update timestamp the cached entry.
    shim_flags (int): shim flags of the cached entry.
    path (str): path of the cached entry.
  """

  def __init__(self):
    """Initializes an Application Compatibility Cache cached entry."""
    super(AppCompatCacheCachedEntry, self).__init__()
    self.cached_entry_size = 0
    self.data = None
    self.file_size = None
    self.insertion_flags = None
    self.last_modification_time = None
    self.last_update_time = None
    self.shim_flags = None
    self.path = None


class AppCompatCacheDataParser(data_format.BinaryDataFormat):
  """Application Compatibility Cache data parser."""

  _DEFINITION_FILE = 'appcompatcache.yaml'

  _FORMAT_TYPE_2000 = 1
  _FORMAT_TYPE_XP = 2
  _FORMAT_TYPE_2003 = 3
  _FORMAT_TYPE_VISTA = 4
  _FORMAT_TYPE_7 = 5
  _FORMAT_TYPE_8 = 6
  _FORMAT_TYPE_10 = 7

  _HEADER_SIGNATURES = {
      # AppCompatCache format signature used in Windows XP.
      0xdeadbeef: _FORMAT_TYPE_XP,
      # AppCompatCache format signature used in Windows 2003, Vista and 2008.
      0xbadc0ffe: _FORMAT_TYPE_2003,
      # AppCompatCache format signature used in Windows 7 and 2008 R2.
      0xbadc0fee: _FORMAT_TYPE_7,
      # AppCompatCache format used in Windows 8.0 and 8.1.
      0x00000080: _FORMAT_TYPE_8,
      # AppCompatCache format used in Windows 10
      0x00000030: _FORMAT_TYPE_10,
      0x00000034: _FORMAT_TYPE_10}

  _HEADER_DATA_TYPE_MAP_NAMES = {
      _FORMAT_TYPE_XP: 'appcompatcache_header_xp_32bit',
      _FORMAT_TYPE_2003: 'appcompatcache_header_2003',
      _FORMAT_TYPE_VISTA: 'appcompatcache_header_vista',
      _FORMAT_TYPE_7: 'appcompatcache_header_7',
      _FORMAT_TYPE_8: 'appcompatcache_header_8',
      _FORMAT_TYPE_10: 'appcompatcache_header_10'}

  _SUPPORTED_FORMAT_TYPES = frozenset(_HEADER_DATA_TYPE_MAP_NAMES.keys())

  # AppCompatCache format used in Windows 8.0.
  _CACHED_ENTRY_SIGNATURE_8_0 = b'00ts'

  # AppCompatCache format used in Windows 8.1.
  _CACHED_ENTRY_SIGNATURE_8_1 = b'10ts'

  def __init__(self, debug=False, output_writer=None):
    """Initializes an Application Compatibility Cache data parser.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(AppCompatCacheDataParser, self).__init__(
        debug=debug, output_writer=output_writer)
    self._cached_entry_data_type_map = None

  def _DebugPrintCachedEntryXP(self, cached_entry):
    """Prints Windows XP AppCompatCache cached entry value debug information.

    Args:
      cached_entry (appcompatcache_cached_entry_xp_32bit): Windows XP
          AppCompatCache cached entry.
    """
    # TODO: have dtFabric handle string conversion.
    string_size = 0
    for string_index in range(0, 528, 2):
      if (cached_entry.path[string_index] == 0 and
          cached_entry.path[string_index + 1] == 0):
        break
      string_size += 2

    path = bytearray(cached_entry.path[0:string_size]).decode('utf-16-le')
    self._DebugPrintValue('Path', path)

    self._DebugPrintDecimalValue('File size', cached_entry.file_size)

    self._DebugPrintFiletimeValue(
        'Last update time', cached_entry.last_update_time)

  def _DebugPrintCachedEntry2003(self, cached_entry):
    """Prints Windows 2003 AppCompatCache cached entry value debug information.

    Args:
      cached_entry_common (appcompatcache_cached_entry_2003_32bit|
                           appcompatcache_cached_entry_2003_64bit|
                           appcompatcache_cached_entry_vista_32bit|
                           appcompatcache_cached_entry_vista_64bit|
                           appcompatcache_cached_entry_7_32bit|
                           appcompatcache_cached_entry_7_64bit): Windows 2003,
          Vista or 7 AppCompatCache cached entry.
    """
    self._DebugPrintDecimalValue('Path size', cached_entry.path_size)

    self._DebugPrintDecimalValue(
        'Maximum path size', cached_entry.maximum_path_size)

    value_string = '0x{0:08x}'.format(cached_entry.path_offset)
    self._DebugPrintValue('Path offset', value_string)

    if hasattr(cached_entry, 'file_size'):
      self._DebugPrintDecimalValue('File size', cached_entry.file_size)

    if hasattr(cached_entry, 'insertion_flags'):
      value_string = '0x{0:08x}'.format(cached_entry.insertion_flags)
      self._DebugPrintValue('Insertion flags', value_string)

    if hasattr(cached_entry, 'shim_flags'):
      value_string = '0x{0:08x}'.format(cached_entry.shim_flags)
      self._DebugPrintValue('Shim flags', value_string)

    if hasattr(cached_entry, 'data_offset'):
      value_string = '0x{0:08x}'.format(cached_entry.data_offset)
      self._DebugPrintValue('Data offset', value_string)

    if hasattr(cached_entry, 'data_size'):
      self._DebugPrintDecimalValue('Data size', cached_entry.data_size)

  def _DebugPrintCachedEntry8(self, cached_entry_header, cached_entry_body):
    """Prints Windows 8 AppCompatCache cached entry value debug information.

    Args:
      cached_entry_header (appcompatcache_cached_entry_header_8): Windows 8 or
          10 AppCompatCache cached entry header.
      cached_entry_body (appcompatcache_cached_entry_header_8_0|
                         appcompatcache_cached_entry_header_8_1|
                         appcompatcache_cached_entry_header_10): Windows 8.0,
          8.1 or 10 AppCompatCache cached entry body.
    """
    self._DebugPrintValue('Signature', cached_entry_header.signature)

    value_string = '0x{0:08x}'.format(cached_entry_header.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintDecimalValue(
        'Cached entry data size', cached_entry_header.cached_entry_data_size)

    self._DebugPrintDecimalValue('Path size', cached_entry_body.path_size)

    self._DebugPrintValue('Path', cached_entry_body.path.rstrip('\x00'))

    if hasattr(cached_entry_body, 'insertion_flags'):
      value_string = '0x{0:08x}'.format(cached_entry_body.insertion_flags)
      self._DebugPrintValue('Insertion flags', value_string)

    if hasattr(cached_entry_body, 'shim_flags'):
      value_string = '0x{0:08x}'.format(cached_entry_body.shim_flags)
      self._DebugPrintValue('Shim flags', value_string)

    if hasattr(cached_entry_body, 'unknown1'):
      value_string = '0x{0:04x}'.format(cached_entry_body.unknown1)
      self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintFiletimeValue(
        'Last modification time', cached_entry_body.last_modification_time)

    self._DebugPrintDecimalValue('Data size', cached_entry_body.data_size)

  def _DebugPrintHeader(self, format_type, header):
    """Prints AppCompatCache header value debug information.

    Args:
      format_type (int): AppCompatCache format type.
      header (appcompatcache_header_xp_32bit|appcompatcache_header_vista|
              appcompatcache_header_7|appcompatcache_header_8|
              appcompatcache_header_10): AppCompatCache header.
    """
    if format_type == self._FORMAT_TYPE_10:
      self._DebugPrintDecimalValue('Header size', header.signature)
    else:
      value_string = '0x{0:08x}'.format(header.signature)
      self._DebugPrintValue('Signature', value_string)

    if format_type in (
        self._FORMAT_TYPE_XP, self._FORMAT_TYPE_2003, self._FORMAT_TYPE_VISTA,
        self._FORMAT_TYPE_7, self._FORMAT_TYPE_10):
      self._DebugPrintDecimalValue(
          'Number of cached entries', header.number_of_cached_entries)

    if format_type == self._FORMAT_TYPE_XP:
      if self._debug:
        value_string = '0x{0:08x}'.format(header.number_of_lru_entries)
        self._DebugPrintValue('Number of LRU entries', value_string)

        value_string = '0x{0:08x}'.format(header.unknown1)
        self._DebugPrintValue('Unknown1', value_string)

    elif format_type == self._FORMAT_TYPE_8:
      value_string = '0x{0:08x}'.format(header.unknown1)
      self._DebugPrintValue('Unknown1', value_string)

    if format_type != self._FORMAT_TYPE_XP:
      self._DebugPrintText('\n')

  def _GetCachedEntryDataTypeMap(
      self, format_type, value_data, cached_entry_offset):
    """Determines the cached entry data type map.

    Args:
      format_type (int): format type.
      value_data (bytes): value data.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.

    Returns:
      dtfabric.DataTypeMap: data type map which contains a data type definition,
          such as a structure, that can be mapped onto binary data or None
          if the data type map is not defined.

    Raises:
      ParseError: if the cached entry data type map cannot be determined.
    """
    if format_type not in self._SUPPORTED_FORMAT_TYPES:
      raise errors.ParseError('Unsupported format type: {0:d}'.format(
          format_type))

    data_type_map_name = ''

    if format_type == self._FORMAT_TYPE_XP:
      data_type_map_name = 'appcompatcache_cached_entry_xp_32bit'

    elif format_type in (self._FORMAT_TYPE_8, self._FORMAT_TYPE_10):
      data_type_map_name = 'appcompatcache_cached_entry_header_8'

    else:
      cached_entry = self._ParseCommon2003CachedEntry(
          value_data, cached_entry_offset)

      # Assume the entry is 64-bit if the 32-bit path offset is 0 and
      # the 64-bit path offset is set.
      if (cached_entry.path_offset_32bit == 0 and
          cached_entry.path_offset_64bit != 0):
        number_of_bits = '64'
      else:
        number_of_bits = '32'

      if format_type == self._FORMAT_TYPE_2003:
        data_type_map_name = (
            'appcompatcache_cached_entry_2003_{0:s}bit'.format(number_of_bits))
      elif format_type == self._FORMAT_TYPE_VISTA:
        data_type_map_name = (
            'appcompatcache_cached_entry_vista_{0:s}bit'.format(number_of_bits))
      elif format_type == self._FORMAT_TYPE_7:
        data_type_map_name = (
            'appcompatcache_cached_entry_7_{0:s}bit'.format(number_of_bits))

    return self._GetDataTypeMap(data_type_map_name)

  def _ParseCommon2003CachedEntry(self, value_data, cached_entry_offset):
    """Parses the cached entry structure common for Windows 2003, Vista and 7.

    Args:
      value_data (bytes): value data.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.

    Returns:
      appcompatcache_cached_entry_2003_common: cached entry structure common
          for Windows 2003, Windows Vista and Windows 7.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    cached_entry_data = value_data[cached_entry_offset:]

    data_type_map = self._GetDataTypeMap(
        'appcompatcache_cached_entry_2003_common')

    try:
      cached_entry = self._ReadStructureFromByteStream(
          cached_entry_data, cached_entry_offset, data_type_map,
          'cached entry')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse cached entry value with error: {0!s}'.format(
              exception))

    if cached_entry.path_size > cached_entry.maximum_path_size:
      raise errors.ParseError('Path size value out of bounds.')

    path_end_of_string_size = (
        cached_entry.maximum_path_size - cached_entry.path_size)
    if cached_entry.path_size == 0 or path_end_of_string_size != 2:
      raise errors.ParseError('Unsupported path size values.')

    return cached_entry

  def CheckSignature(self, value_data):
    """Parses and validates the signature.

    Args:
      value_data (bytes): value data.

    Returns:
      int: format type or None if format could not be determined.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('uint32le')

    try:
      signature = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'signature')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse signature value with error: {0!s}'.format(
              exception))

    format_type = self._HEADER_SIGNATURES.get(signature, None)

    if format_type == self._FORMAT_TYPE_2003:
      # TODO: determine which format version is used (2003 or Vista).
      return self._FORMAT_TYPE_2003

    elif format_type == self._FORMAT_TYPE_8:
      cached_entry_signature = value_data[signature:signature + 4]
      if cached_entry_signature in (
          self._CACHED_ENTRY_SIGNATURE_8_0, self._CACHED_ENTRY_SIGNATURE_8_1):
        return self._FORMAT_TYPE_8

    elif format_type == self._FORMAT_TYPE_10:
      # Windows 10 uses the same cache entry signature as Windows 8.1
      cached_entry_signature = value_data[signature:signature + 4]
      if cached_entry_signature == self._CACHED_ENTRY_SIGNATURE_8_1:
        return self._FORMAT_TYPE_10

    return format_type

  def ParseCachedEntry(
      self, format_type, value_data, cached_entry_index, cached_entry_offset):
    """Parses a cached entry.

    Args:
      format_type (int): format type.
      value_data (bytes): value data.
      cached_entry_index (int): cached entry index.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.

    Returns:
      AppCompatCacheCachedEntry: cached entry.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if not self._cached_entry_data_type_map:
      self._cached_entry_data_type_map = self._GetCachedEntryDataTypeMap(
          format_type, value_data, cached_entry_offset)

    if not self._cached_entry_data_type_map:
      raise errors.ParseError('Unable to determine cached entry data type.')

    cached_entry_size = self._cached_entry_data_type_map.GetByteSize()
    cached_entry_end_offset = cached_entry_offset + cached_entry_size
    cached_entry_data = value_data[cached_entry_offset:cached_entry_end_offset]

    if self._debug:
      if format_type not in (self._FORMAT_TYPE_8, self._FORMAT_TYPE_10):
        description = 'Cached entry: {0:d} data'.format(cached_entry_index)
        self._DebugPrintData(description, cached_entry_data)

    try:
      cached_entry = self._ReadStructureFromByteStream(
          cached_entry_data, cached_entry_offset,
          self._cached_entry_data_type_map, 'cached entry')
    except (ValueError, errors.ParseError) as exception:
      if self._debug:
        if format_type in (self._FORMAT_TYPE_8, self._FORMAT_TYPE_10):
          description = 'Cached entry: {0:d} header data'.format(
              cached_entry_index)
          self._DebugPrintData(description, cached_entry_data)

      raise errors.ParseError(
          'Unable to parse cached entry value with error: {0!s}'.format(
              exception))

    if format_type in (self._FORMAT_TYPE_8, self._FORMAT_TYPE_10):
      if cached_entry.signature not in (
          self._CACHED_ENTRY_SIGNATURE_8_0, self._CACHED_ENTRY_SIGNATURE_8_1):
        if self._debug:
          description = 'Cached entry: {0:d} header data'.format(
              cached_entry_index)
          self._DebugPrintData(description, cached_entry_data)

        raise errors.ParseError('Unsupported cache entry signature')

    cached_entry_object = AppCompatCacheCachedEntry()

    data_offset = 0
    data_size = 0

    if format_type == self._FORMAT_TYPE_XP:
      if self._debug:
        self._DebugPrintCachedEntryXP(cached_entry)

      # TODO: have dtFabric handle string conversion.
      string_size = 0
      for string_index in range(0, 528, 2):
        if (cached_entry.path[string_index] == 0 and
            cached_entry.path[string_index + 1] == 0):
          break
        string_size += 2

      last_modification_time = cached_entry.last_modification_time
      path = bytearray(cached_entry.path[0:string_size]).decode('utf-16-le')

      cached_entry_object.last_update_time = cached_entry.last_update_time

    elif format_type in (
        self._FORMAT_TYPE_2003, self._FORMAT_TYPE_VISTA, self._FORMAT_TYPE_7):
      if self._debug:
        self._DebugPrintCachedEntry2003(cached_entry)

      last_modification_time = cached_entry.last_modification_time

      if format_type in (self._FORMAT_TYPE_VISTA, self._FORMAT_TYPE_7):
        cached_entry_object.insertion_flags = cached_entry.insertion_flags
        cached_entry_object.shim_flags = cached_entry.shim_flags

      path_size = cached_entry.path_size
      maximum_path_size = cached_entry.maximum_path_size
      path_offset = cached_entry.path_offset

      if path_offset > 0 and path_size > 0:
        path_size += path_offset
        maximum_path_size += path_offset

        if self._debug:
          self._DebugPrintData(
              'Path data', value_data[path_offset:maximum_path_size])

        path = value_data[path_offset:path_size].decode('utf-16-le')

        if self._debug:
          self._DebugPrintValue('Path', path)

      if format_type == self._FORMAT_TYPE_7:
        data_offset = cached_entry.data_offset
        data_size = cached_entry.data_size

    elif format_type in (self._FORMAT_TYPE_8, self._FORMAT_TYPE_10):
      cached_entry_data_size = cached_entry.cached_entry_data_size
      cached_entry_size = 12 + cached_entry_data_size
      cached_entry_end_offset = cached_entry_offset + cached_entry_size

      cached_entry_data = value_data[
          cached_entry_offset:cached_entry_end_offset]

      if self._debug:
        description = 'Cached entry: {0:d} data'.format(cached_entry_index)
        self._DebugPrintData(description, cached_entry_data)

      if format_type == self._FORMAT_TYPE_10:
        data_type_map_name = 'appcompatcache_cached_entry_body_10'
      elif cached_entry.signature == self._CACHED_ENTRY_SIGNATURE_8_0:
        data_type_map_name = 'appcompatcache_cached_entry_body_8_0'
      elif cached_entry.signature == self._CACHED_ENTRY_SIGNATURE_8_1:
        data_type_map_name = 'appcompatcache_cached_entry_body_8_1'

      data_type_map = self._GetDataTypeMap(data_type_map_name)
      context = dtfabric_data_maps.DataTypeMapContext()

      try:
        cached_entry_body = self._ReadStructureFromByteStream(
            cached_entry_data[12:], cached_entry_offset + 12,
            data_type_map, 'cached entry body', context=context)
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError(
            'Unable to parse cached entry body with error: {0!s}'.format(
                exception))

      if self._debug:
        self._DebugPrintCachedEntry8(cached_entry, cached_entry_body)

      last_modification_time = cached_entry_body.last_modification_time
      path = cached_entry_body.path

      if format_type == self._FORMAT_TYPE_8:
        cached_entry_object.insertion_flags = cached_entry_body.insertion_flags
        cached_entry_object.shim_flags = cached_entry_body.shim_flags

      data_offset = cached_entry_offset + context.byte_size
      data_size = cached_entry_body.data_size

    if self._debug:
      self._DebugPrintText('\n')

    cached_entry_object.cached_entry_size = cached_entry_size
    cached_entry_object.file_size = getattr(cached_entry, 'file_size', None)
    cached_entry_object.last_modification_time = last_modification_time
    cached_entry_object.path = path

    if data_size > 0:
      cached_entry_object.data = value_data[data_offset:data_offset + data_size]

      if self._debug:
        self._DebugPrintData('Data', cached_entry_object.data)

    return cached_entry_object

  def ParseHeader(self, format_type, value_data):
    """Parses the header.

    Args:
      format_type (int): format type.
      value_data (bytes): value data.

    Returns:
      AppCompatCacheHeader: header.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map_name = self._HEADER_DATA_TYPE_MAP_NAMES.get(format_type, None)
    if not data_type_map_name:
      raise errors.ParseError(
          'Unsupported format type: {0:d}'.format(format_type))

    data_type_map = self._GetDataTypeMap(data_type_map_name)

    try:
      header = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'header')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse header value with error: {0!s}'.format(
              exception))

    header_data_size = data_type_map.GetByteSize()
    if format_type == self._FORMAT_TYPE_10:
      header_data_size = header.signature

    cache_header = AppCompatCacheHeader()
    cache_header.header_size = header_data_size
    cache_header.number_of_cached_entries = getattr(
        header, 'number_of_cached_entries', None)

    if self._debug:
      self._DebugPrintHeader(format_type, header)

    if format_type == self._FORMAT_TYPE_XP:
      if self._debug:
        self._DebugPrintText('LRU entries:')

      data_offset = 16
      number_of_lru_entries = header.number_of_lru_entries
      if number_of_lru_entries > 0 and number_of_lru_entries <= 96:
        data_type_map = self._GetDataTypeMap('uint32le')

        for lru_entry_index in range(number_of_lru_entries):
          try:
            lru_entry = self._ReadStructureFromByteStream(
                value_data[data_offset:data_offset + 4], data_offset,
                data_type_map, 'LRU entry')
          except (ValueError, errors.ParseError) as exception:
            raise errors.ParseError(
                'Unable to parse LRU entry value with error: {0!s}'.format(
                    exception))

          data_offset += 4

          if self._debug:
            description = 'LRU entry: {0:d}'.format(lru_entry_index)
            value_string = '{0:d} (offset: 0x{1:08x})'.format(
                lru_entry, 400 + (lru_entry * 552))
            self._DebugPrintValue(description, value_string)

        if self._debug:
          self._DebugPrintText('\n')

      if self._debug:
        self._DebugPrintData('Unknown data', value_data[data_offset:400])

    self._cached_entry_data_type_map = None

    return cache_header


class AppCompatCacheCollector(interface.WindowsRegistryKeyCollector):
  """Application Compatibility Cache collector.

  Attributes:
    cached_entries (list[AppCompatCacheCachedEntry]): cached entries.
  """

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Application Compatibility Cache collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(AppCompatCacheCollector, self).__init__(debug=debug)
    self._parser = AppCompatCacheDataParser(
        debug=self._debug, output_writer=output_writer)
    self._output_writer = output_writer
    self.cached_entries = []

  def _CollectAppCompatCacheFromKey(self, app_compat_cache_key):
    """Collects Application Compatibility Cache from a Windows Registry key.

    Args:
      app_compat_cache_key (dfwinreg.WinRegistryKey): Application Compatibility
          Cache Windows Registry key.

    Returns:
      bool: True if the Application Compatibility Cache key was found,
          False if not.
    """
    value = app_compat_cache_key.GetValueByName('AppCompatCache')
    if not value:
      logging.warning('Missing AppCompatCache value in key: {0:s}'.format(
          app_compat_cache_key.path))
      return True

    value_data = value.data
    value_data_size = len(value.data)

    # TODO: add non debug output
    if self._debug:
      self._output_writer.WriteDebugData('Value data:\n', value_data)

    format_type = self._parser.CheckSignature(value_data)
    if not format_type:
      logging.warning('Unsupported signature.')
      return True

    cache_header = self._parser.ParseHeader(format_type, value_data)

    # On Windows Vista and 2008 when the cache is empty it will
    # only consist of the header.
    if value_data_size <= cache_header.header_size:
      return True

    cached_entry_offset = cache_header.header_size
    cached_entry_index = 0

    while cached_entry_offset < value_data_size:
      cached_entry = self._parser.ParseCachedEntry(
          format_type, value_data, cached_entry_index, cached_entry_offset)

      self.cached_entries.append(cached_entry)

      cached_entry_offset += cached_entry.cached_entry_size
      cached_entry_index += 1

      if (cache_header.number_of_cached_entries != 0 and
          cached_entry_index >= cache_header.number_of_cached_entries):
        break

    return True

  def Collect(self, registry, all_control_sets=False):  # pylint: disable=arguments-differ
    """Collects the Application Compatibility Cache.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      all_control_sets (Optional[bool]): True if the services should be
          collected from all control sets instead of only the current control
          set.

    Returns:
      bool: True if the Application Compatibility Cache key was found,
          False if not.
    """
    result = False

    if all_control_sets:
      system_key = registry.GetKeyByPath('HKEY_LOCAL_MACHINE\\System\\')
      if not system_key:
        return result

      for control_set_key in system_key.GetSubkeys():
        if control_set_key.name.startswith('ControlSet'):
          # Windows XP
          app_compat_cache_key = control_set_key.GetSubkeyByPath(
              'Control\\Session Manager\\AppCompatibility')
          if app_compat_cache_key:
            if self._CollectAppCompatCacheFromKey(app_compat_cache_key):
              result = True

          # Windows 2003 and later
          app_compat_cache_key = control_set_key.GetSubkeyByPath(
              'Control\\Session Manager\\AppCompatCache')
          if app_compat_cache_key:
            if self._CollectAppCompatCacheFromKey(app_compat_cache_key):
              result = True
    else:
      # Windows XP
      key_path = (
          'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\'
          'Session Manager\\AppCompatibility')
      app_compat_cache_key = registry.GetKeyByPath(key_path)
      if app_compat_cache_key:
        if self._CollectAppCompatCacheFromKey(app_compat_cache_key):
          result = True

      # Windows 2003 and later
      key_path = (
          'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\'
          'Session Manager\\AppCompatCache')
      app_compat_cache_key = registry.GetKeyByPath(key_path)
      if app_compat_cache_key:
        if self._CollectAppCompatCacheFromKey(app_compat_cache_key):
          result = True

    return result
