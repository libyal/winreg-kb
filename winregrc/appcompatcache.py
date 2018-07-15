# -*- coding: utf-8 -*-
"""Application Compatibility Cache collector."""

from __future__ import unicode_literals

import logging

from dtfabric import errors as dtfabric_errors

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

  FORMAT_TYPE_2000 = 1
  FORMAT_TYPE_XP = 2
  FORMAT_TYPE_2003 = 3
  FORMAT_TYPE_VISTA = 4
  FORMAT_TYPE_7 = 5
  FORMAT_TYPE_8 = 6
  FORMAT_TYPE_10 = 7

  _DEFINITION_FILE = 'appcompatcache.yaml'

  _HEADER_SIGNATURES = {
      # AppCompatCache format signature used in Windows XP.
      0xdeadbeef: FORMAT_TYPE_XP,
      # AppCompatCache format signature used in Windows 2003, Vista and 2008.
      0xbadc0ffe: FORMAT_TYPE_2003,
      # AppCompatCache format signature used in Windows 7 and 2008 R2.
      0xbadc0fee: FORMAT_TYPE_7,
      # AppCompatCache format used in Windows 8.0 and 8.1.
      0x00000080: FORMAT_TYPE_8,
      # AppCompatCache format used in Windows 10
      0x00000030: FORMAT_TYPE_10,
      0x00000034: FORMAT_TYPE_10}

  _HEADER_DATA_TYPE_MAP_NAMES = {
      FORMAT_TYPE_XP: 'appcompatcache_header_xp_32bit',
      FORMAT_TYPE_2003: 'appcompatcache_header_2003',
      FORMAT_TYPE_VISTA: 'appcompatcache_header_vista',
      FORMAT_TYPE_7: 'appcompatcache_header_7',
      FORMAT_TYPE_8: 'appcompatcache_header_8',
      FORMAT_TYPE_10: 'appcompatcache_header_10'}

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

  def _DebugPrintCachedEntry(self, format_type, cached_entry):
    """Prints AppCompatCache cached entry value debug information.

    Args:
      format_type (int): AppCompatCache format type.
      cached_entry (appcompatcache_cached_entry_xp_32bit|
                    appcompatcache_cached_entry_2003_common|
                    appcompatcache_cached_entry_2003_32bit|
                    appcompatcache_cached_entry_2003_64bit|
                    appcompatcache_cached_entry_vista_32bit|
                    appcompatcache_cached_entry_vista_64bit|
                    appcompatcache_cached_entry_7_32bit|
                    appcompatcache_cached_entry_7_64bit|
                    appcompatcache_cached_entry_header_8): AppCompatCache
          cached entry.
    """

  def _DebugPrintHeader(self, format_type, header):
    """Prints AppCompatCache header value debug information.

    Args:
      format_type (int): AppCompatCache format type.
      header (appcompatcache_header_xp_32bit|appcompatcache_header_vista|
              appcompatcache_header_7|appcompatcache_header_8|
              appcompatcache_header_10): AppCompatCache header.
    """
    if format_type == self.FORMAT_TYPE_10:
      self._DebugPrintDecimalValue('Header size', header.signature)
    else:
      value_string = '0x{0:08x}'.format(header.signature)
      self._DebugPrintValue('Signature', value_string)

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_10):
      self._DebugPrintDecimalValue(
          'Number of cached entries', header.number_of_cached_entries)

    if format_type == self.FORMAT_TYPE_XP:
      if self._debug:
        value_string = '0x{0:08x}'.format(header.number_of_lru_entries)
        self._DebugPrintValue('Number of LRU entries', value_string)

        value_string = '0x{0:08x}'.format(header.unknown1)
        self._DebugPrintValue('Unknown1', value_string)

    elif format_type == self.FORMAT_TYPE_8:
      value_string = '0x{0:08x}'.format(header.unknown1)
      self._DebugPrintValue('Unknown1', value_string)

    if format_type != self.FORMAT_TYPE_XP:
      self._DebugPrintText('')

  def _GetCachedEntryDataTypeMap(
      self, format_type, value_data, cached_entry_offset):
    """Determines the cached entry data type map.

    Args:
      format_type (int): format type.
      value_data (bytess): value data.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.

    Returns:
      dtfabric.DataTypeMap: data type map which contains a data type definition,
          such as a structure, that can be mapped onto binary data.

    Raises:
      ParseError: if the cached entry data type map cannot be determined.
    """
    if format_type not in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      raise errors.ParseError(
          'Unsupported format type: {0:d}'.format(format_type))

    data_type_map_name = ''

    if format_type == self.FORMAT_TYPE_XP:
      data_type_map_name = 'appcompatcache_cached_entry_xp_32bit'

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      data_type_map_name = 'appcompatcache_cached_entry_header_8'

    else:
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
        errors.ParseError('Path size value out of bounds.')
        return None

      path_end_of_string_size = (
          cached_entry.maximum_path_size - cached_entry.path_size)
      if cached_entry.path_size == 0 or path_end_of_string_size != 2:
        errors.ParseError('Unsupported path size values.')
        return None

      # Assume the entry is 64-bit if the 32-bit path offset is 0 and
      # the 64-bit path offset is set.
      if (cached_entry.path_offset_32bit == 0 and
          cached_entry.path_offset_64bit != 0):
        if format_type == self.FORMAT_TYPE_2003:
          data_type_map_name = 'appcompatcache_cached_entry_2003_64bit'
        elif format_type == self.FORMAT_TYPE_VISTA:
          data_type_map_name = 'appcompatcache_cached_entry_vista_64bit'
        elif format_type == self.FORMAT_TYPE_7:
          data_type_map_name = 'appcompatcache_cached_entry_7_64bit'

      else:
        if format_type == self.FORMAT_TYPE_2003:
          data_type_map_name = 'appcompatcache_cached_entry_2003_32bit'
        elif format_type == self.FORMAT_TYPE_VISTA:
          data_type_map_name = 'appcompatcache_cached_entry_vista_32bit'
        elif format_type == self.FORMAT_TYPE_7:
          data_type_map_name = 'appcompatcache_cached_entry_7_32bit'

    return self._GetDataTypeMap(data_type_map_name)

  def CheckSignature(self, value_data):
    """Parses the signature.

    Args:
      value_data (bytes): value data.

    Returns:
      int: format type or None.

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

    if format_type == self.FORMAT_TYPE_2003:
      # TODO: determine which format version is used (2003 or Vista).
      return self.FORMAT_TYPE_2003

    elif format_type == self.FORMAT_TYPE_8:
      cached_entry_signature = value_data[signature:signature + 4]
      if cached_entry_signature in (
          self._CACHED_ENTRY_SIGNATURE_8_0, self._CACHED_ENTRY_SIGNATURE_8_1):
        return self.FORMAT_TYPE_8

    elif format_type == self.FORMAT_TYPE_10:
      # Windows 10 uses the same cache entry signature as Windows 8.1
      cached_entry_signature = value_data[signature:signature + 4]
      if cached_entry_signature == self._CACHED_ENTRY_SIGNATURE_8_1:
        return self.FORMAT_TYPE_10

    return format_type

  def ParseCachedEntry(
      self, format_type, value_data, cached_entry_index, cached_entry_offset):
    """Parses a cached entry.

    Args:
      format_type (int): format type.
      value_data (bytess): value data.
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
      if format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
        description = 'Cached entry: {0:d} header data:'.format(
            cached_entry_index)
        self._DebugPrintData(description, cached_entry_data[:-2])
      else:
        description = 'Cached entry: {0:d} data:'.format(cached_entry_index)
        self._DebugPrintData(description, cached_entry_data)

    if format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      if cached_entry_data[0:4] not in (
          self._CACHED_ENTRY_SIGNATURE_8_0, self._CACHED_ENTRY_SIGNATURE_8_1):
        raise errors.ParseError('Unsupported cache entry signature')

    try:
      cached_entry = self._ReadStructureFromByteStream(
          cached_entry_data, cached_entry_offset,
          self._cached_entry_data_type_map, 'cached entry')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse cached entry value with error: {0!s}'.format(
              exception))

    if format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      cached_entry_data_size = cached_entry.cached_entry_data_size
      cached_entry_size = 12 + cached_entry_data_size
      cached_entry_end_offset = cached_entry_offset + cached_entry_size

      cached_entry_data = value_data[
          cached_entry_offset:cached_entry_end_offset]

      if self._debug:
        description = 'Cached entry: {0:d} data:'.format(cached_entry_index)
        self._DebugPrintData(description, cached_entry_data)

    cached_entry_object = AppCompatCacheCachedEntry()
    cached_entry_object.cached_entry_size = cached_entry_size

    path_offset = 0
    data_size = 0

    if format_type == self.FORMAT_TYPE_XP:
      string_size = 0
      for string_index in range(0, 528, 2):
        if (cached_entry_data[string_index] == '\0' and
            cached_entry_data[string_index + 1] == '\0'):
          break
        string_size += 2

      cached_entry_object.path = cached_entry_data[0:string_size].decode(
          'utf-16-le')

      if self._debug:
        self._DebugPrintValue('Path', cached_entry_object.path)

    elif format_type in (
        self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA, self.FORMAT_TYPE_7):
      path_size = cached_entry.path_size
      maximum_path_size = cached_entry.maximum_path_size
      path_offset = cached_entry.path_offset

      if self._debug:
        self._DebugPrintDecimalValue('Path size', path_size)

        self._DebugPrintDecimalValue('Maximum path size', maximum_path_size)

        value_string = '0x{0:08x}'.format(path_offset)
        self._DebugPrintValue('Path offset', value_string)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      path_size = cached_entry.path_size

      if self._debug:
        self._DebugPrintValue('Signature', cached_entry_data[0:4])

        value_string = '0x{0:08x}'.format(cached_entry.unknown1)
        self._DebugPrintValue('Unknown1', value_string)

        self._DebugPrintDecimalValue(
            'Cached entry data size', cached_entry_data_size)

        self._DebugPrintDecimalValue('Path size', path_size)

      cached_entry_data_offset = 14 + path_size
      cached_entry_object.path = cached_entry_data[
          14:cached_entry_data_offset].decode('utf-16-le')

      if self._debug:
        self._DebugPrintValue('Path', cached_entry_object.path)

      if format_type == self.FORMAT_TYPE_8:
        remaining_data = cached_entry_data[cached_entry_data_offset:]

        data_type_map = self._GetDataTypeMap('uint32le')

        try:
          insertion_flags = self._ReadStructureFromByteStream(
              remaining_data[0:4], cached_entry_data_offset, data_type_map,
              'insertion flags')
        except (ValueError, errors.ParseError) as exception:
          raise errors.ParseError(
              'Unable to parse insertion flags value with error: {0!s}'.format(
                  exception))

        try:
          shim_flags = self._ReadStructureFromByteStream(
              remaining_data[4:8], cached_entry_data_offset + 4, data_type_map,
              'shim flags')
        except (ValueError, errors.ParseError) as exception:
          raise errors.ParseError(
              'Unable to parse shim flags value with error: {0!s}'.format(
                  exception))

        if self._debug:
          value_string = '0x{0:08x}'.format(insertion_flags)
          self._DebugPrintValue('Insertion flags', value_string)

          value_string = '0x{0:08x}'.format(shim_flags)
          self._DebugPrintValue('Shim flags', value_string)

        cached_entry_object.insertion_flags = insertion_flags
        cached_entry_object.shim_flags = shim_flags

        if cached_entry_data[0:4] == self._CACHED_ENTRY_SIGNATURE_8_0:
          cached_entry_data_offset += 8

        elif cached_entry_data[0:4] == self._CACHED_ENTRY_SIGNATURE_8_1:
          if self._debug:
            data_type_map = self._GetDataTypeMap('uint16le')

            try:
              unknown1 = self._ReadStructureFromByteStream(
                  remaining_data[8:10], 8, data_type_map, 'unknown1')
            except (ValueError, errors.ParseError) as exception:
              raise errors.ParseError(
                  'Unable to parse unknown1 value with error: {0!s}'.format(
                      exception))

            value_string = '0x{0:04x}'.format(unknown1)
            self._DebugPrintValue('Unknown1', value_string)

          cached_entry_data_offset += 10

      remaining_data = cached_entry_data[cached_entry_data_offset:]

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7):
      cached_entry_object.last_modification_time = (
          cached_entry.last_modification_time)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      data_type_map = self._GetDataTypeMap('uint64le')

      try:
        timestamp = self._ReadStructureFromByteStream(
            remaining_data[0:8], 0, data_type_map, 'last modification time')
      except (ValueError, errors.ParseError) as exception:
        raise errors.ParseError((
            'Unable to parse last modification time value with error: '
            '{0!s}').format(exception))

      cached_entry_object.last_modification_time = timestamp

    if self._debug:
      self._DebugPrintFiletimeValue(
          'Last modification time', cached_entry_object.last_modification_time)

    if format_type in (self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003):
      cached_entry_object.file_size = cached_entry.file_size

      if self._debug:
        self._DebugPrintDecimalValue('File size', cached_entry_object.file_size)

    elif format_type in (self.FORMAT_TYPE_VISTA, self.FORMAT_TYPE_7):
      cached_entry_object.insertion_flags = cached_entry.insertion_flags
      cached_entry_object.shim_flags = cached_entry.shim_flags

      if self._debug:
        value_string = '0x{0:08x}'.format(cached_entry_object.insertion_flags)
        self._DebugPrintValue('Insertion flags', value_string)

        value_string = '0x{0:08x}'.format(cached_entry_object.shim_flags)
        self._DebugPrintValue('Shim flags', value_string)

    if format_type == self.FORMAT_TYPE_XP:
      cached_entry_object.last_update_time = cached_entry.last_update_time

      if self._debug:
        self._DebugPrintFiletimeValue(
            'Last update time', cached_entry_object.last_update_time)

    if format_type == self.FORMAT_TYPE_7:
      data_offset = cached_entry.data_offset
      data_size = cached_entry.data_size

      if self._debug:
        value_string = '0x{0:08x}'.format(data_offset)
        self._DebugPrintValue('Data offset', value_string)

        self._DebugPrintDecimalValue('Data size', data_size)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      data_offset = cached_entry_offset + cached_entry_data_offset + 12
      data_type_map = self._GetDataTypeMap('uint32le')

      try:
        data_size = data_type_map.MapByteStream(remaining_data[8:12])
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      if self._debug:
        self._DebugPrintDecimalValue('Data size', data_size)

    if self._debug:
      self._DebugPrintText('')

    if path_offset > 0 and path_size > 0:
      path_size += path_offset
      maximum_path_size += path_offset

      if self._debug:
        self._DebugPrintData(
            'Path data', value_data[path_offset:maximum_path_size])

      cached_entry_object.path = value_data[path_offset:path_size].decode(
          'utf-16-le')

      if self._debug:
        self._DebugPrintValue('Path', cached_entry_object.path)
        self._DebugPrintText('')

    if data_size > 0:
      data_size += data_offset

      cached_entry_object.data = value_data[data_offset:data_size]

      if self._debug:
        self._DebugPrintData('Data:', cached_entry_object.data)

    return cached_entry_object

  def ParseHeader(self, format_type, value_data):
    """Parses the header.

    Args:
      format_type (int): format type.
      value_data (bytess): value data.

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
    if format_type == self.FORMAT_TYPE_10:
      header_data_size = header.signature

    cache_header = AppCompatCacheHeader()
    cache_header.header_size = header_data_size

    if self._debug:
      self._DebugPrintHeader(format_type, header)

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_10):
      cache_header.number_of_cached_entries = header.number_of_cached_entries

    if format_type == self.FORMAT_TYPE_XP:
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
          self._DebugPrintText('')

      if self._debug:
        self._DebugPrintData('Unknown data:', value_data[data_offset:400])

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
