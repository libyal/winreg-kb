# -*- coding: utf-8 -*-
"""Application Compatibility Cache collector."""

import datetime
import logging

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

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


class AppCompatCacheDataParser(object):
  """Application Compatibility Cache data parser."""

  FORMAT_TYPE_2000 = 1
  FORMAT_TYPE_XP = 2
  FORMAT_TYPE_2003 = 3
  FORMAT_TYPE_VISTA = 4
  FORMAT_TYPE_7 = 5
  FORMAT_TYPE_8 = 6
  FORMAT_TYPE_10 = 7

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: byte',
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
      b'name: uint64',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: uint16le',
      b'type: integer',
      b'attributes:',
      b'  byte_order: little-endian',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: uint32le',
      b'type: integer',
      b'attributes:',
      b'  byte_order: little-endian',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint64le',
      b'type: integer',
      b'attributes:',
      b'  byte_order: little-endian',
      b'  format: unsigned',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: appcompatcache_header_xp_32bit',
      b'type: structure',
      b'description: Windows XP 32-bit AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: number_of_cached_entries',
      b'  data_type: uint32',
      b'- name: number_of_lru_entries',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: lru_entries',
      b'  type: sequence',
      b'  element_data_type: uint32',
      b'  number_of_elements: 96',
      b'---',
      b'name: appcompatcache_cached_entry_xp_32bit',
      b'type: structure',
      b'description: Windows XP 32-bit AppCompatCache cached entry.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 528',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: file_size',
      b'  data_type: uint64',
      b'- name: last_update_time',
      b'  data_type: uint64',
      b'---',
      b'name: appcompatcache_header_2003',
      b'type: structure',
      b'description: Windows 2003 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: number_of_cached_entries',
      b'  data_type: uint32',
      b'---',
      b'name: appcompatcache_cached_entry_2003_common',
      b'type: structure',
      (b'description: Windows 2003, Vista, 7 common AppCompatCache cached '
       b'entry.'),
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: path_offset_32bit',
      b'  data_type: uint32',
      b'- name: path_offset_64bit',
      b'  data_type: uint64',
      b'---',
      b'name: appcompatcache_cached_entry_2003_32bit',
      b'type: structure',
      b'description: Windows 2003 32-bit AppCompatCache cached entry.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: path_offset',
      b'  data_type: uint32',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: file_size',
      b'  data_type: uint64',
      b'---',
      b'name: appcompatcache_cached_entry_2003_64bit',
      b'type: structure',
      b'description: Windows 2003 64-bit AppCompatCache cached entry.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: path_offset',
      b'  data_type: uint64',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: file_size',
      b'  data_type: uint64',
      b'---',
      b'name: appcompatcache_header_vista',
      b'type: structure',
      b'description: Windows Vista and 2008 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: number_of_cached_entries',
      b'  data_type: uint32',
      b'---',
      b'name: appcompatcache_cached_entry_vista_32bit',
      b'type: structure',
      (b'description: Windows Vista and 2008 32-bit AppCompatCache '
       b'cached entry.'),
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: path_offset',
      b'  data_type: uint32',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: insertion_flags',
      b'  data_type: uint32',
      b'- name: shim_flags',
      b'  data_type: uint32',
      b'---',
      b'name: appcompatcache_cached_entry_vista_64bit',
      b'type: structure',
      (b'description: Windows Vista and 2008 64-bit AppCompatCache '
       b'cached entry.'),
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: path_offset',
      b'  data_type: uint64',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: insertion_flags',
      b'  data_type: uint32',
      b'- name: shim_flags',
      b'  data_type: uint32',
      b'---',
      b'name: appcompatcache_header_7',
      b'type: structure',
      b'description: Windows 7 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: number_of_cached_entries',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 120',
      b'---',
      b'name: appcompatcache_cached_entry_7_32bit',
      b'type: structure',
      b'description: Windows 7 and 2008 R2 32-bit AppCompatCache cached entry.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: path_offset',
      b'  data_type: uint32',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: insertion_flags',
      b'  data_type: uint32',
      b'- name: shim_flags',
      b'  data_type: uint32',
      b'- name: data_size',
      b'  data_type: uint32',
      b'- name: data_offset',
      b'  data_type: uint32',
      b'---',
      b'name: appcompatcache_cached_entry_7_64bit',
      b'type: structure',
      b'description: Windows 7 and 2008 R2 64-bit AppCompatCache cached entry.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: path_size',
      b'  data_type: uint16',
      b'- name: maximum_path_size',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: path_offset',
      b'  data_type: uint64',
      b'- name: last_modification_time',
      b'  data_type: uint64',
      b'- name: insertion_flags',
      b'  data_type: uint64',
      b'- name: shim_flags',
      b'  data_type: uint64',
      b'---',
      b'name: appcompatcache_header_8',
      b'type: structure',
      b'description: Windows 8 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: unknown2',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 120',
      b'---',
      b'name: appcompatcache_cached_entry_header_8',
      b'type: structure',
      b'description: Windows 8 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: cached_entry_data_size',
      b'  data_type: uint32',
      b'- name: path_size',
      b'  data_type: uint16',
      b'---',
      b'name: appcompatcache_header_10',
      b'type: structure',
      b'description: Windows 10 AppCompatCache header.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: signature',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: unknown2',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 28',
      b'- name: number_of_cached_entries',
      b'  data_type: uint32',
      b'- name: unknown3',
      b'  type: sequence',
      b'  element_data_type: byte',
      b'  number_of_elements: 8'
  ])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _UINT16LE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'uint16le')
  _UINT32LE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'uint32le')
  _UINT64LE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'uint64le')

  _HEADER_XP_32BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_xp_32bit')

  _CACHED_ENTRY_XP_32BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_xp_32bit')

  _CACHED_ENTRY_XP_32BIT_SIZE = _CACHED_ENTRY_XP_32BIT.GetByteSize()

  _HEADER_2003 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_2003')

  _CACHED_ENTRY_2003_COMMON = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_2003_common')

  _CACHED_ENTRY_2003_32BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_2003_32bit')

  _CACHED_ENTRY_2003_32BIT_SIZE = _CACHED_ENTRY_2003_32BIT.GetByteSize()

  _CACHED_ENTRY_2003_64BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_2003_64bit')

  _CACHED_ENTRY_2003_64BIT_SIZE = _CACHED_ENTRY_2003_64BIT.GetByteSize()

  _HEADER_VISTA = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_vista')

  _CACHED_ENTRY_VISTA_32BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_vista_32bit')

  _CACHED_ENTRY_VISTA_32BIT_SIZE = _CACHED_ENTRY_VISTA_32BIT.GetByteSize()

  _CACHED_ENTRY_VISTA_64BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_vista_64bit')

  _CACHED_ENTRY_VISTA_64BIT_SIZE = _CACHED_ENTRY_VISTA_64BIT.GetByteSize()

  _HEADER_7 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_7')

  _CACHED_ENTRY_7_32BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_7_32bit')

  _CACHED_ENTRY_7_32BIT_SIZE = _CACHED_ENTRY_7_32BIT.GetByteSize()

  _CACHED_ENTRY_7_64BIT = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_7_64bit')

  _CACHED_ENTRY_7_64BIT_SIZE = _CACHED_ENTRY_7_64BIT.GetByteSize()

  _HEADER_8 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_8')

  _CACHED_ENTRY_HEADER_8 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_cached_entry_header_8')

  _CACHED_ENTRY_HEADER_8_SIZE = _CACHED_ENTRY_HEADER_8.GetByteSize()

  _HEADER_10 = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'appcompatcache_header_10')

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

  _HEADERS = {
      FORMAT_TYPE_XP: _HEADER_XP_32BIT,
      FORMAT_TYPE_2003: _HEADER_2003,
      FORMAT_TYPE_VISTA: _HEADER_VISTA,
      FORMAT_TYPE_7: _HEADER_7,
      FORMAT_TYPE_8: _HEADER_8,
      FORMAT_TYPE_10: _HEADER_10}

  _HEADER_SIZES = {
      FORMAT_TYPE_XP: _HEADER_XP_32BIT.GetByteSize(),
      FORMAT_TYPE_2003: _HEADER_2003.GetByteSize(),
      FORMAT_TYPE_VISTA: _HEADER_VISTA.GetByteSize(),
      FORMAT_TYPE_7: _HEADER_7.GetByteSize(),
      FORMAT_TYPE_8: _HEADER_8.GetByteSize(),
      FORMAT_TYPE_10: _HEADER_10.GetByteSize()}

  _CACHED_ENTRIES = {
      FORMAT_TYPE_XP: {
          _CACHED_ENTRY_XP_32BIT_SIZE: _CACHED_ENTRY_XP_32BIT},
      FORMAT_TYPE_2003: {
          _CACHED_ENTRY_2003_32BIT_SIZE: _CACHED_ENTRY_2003_32BIT,
          _CACHED_ENTRY_2003_64BIT_SIZE: _CACHED_ENTRY_2003_64BIT},
      FORMAT_TYPE_VISTA: {
          _CACHED_ENTRY_VISTA_32BIT_SIZE: _CACHED_ENTRY_VISTA_32BIT,
          _CACHED_ENTRY_VISTA_64BIT_SIZE: _CACHED_ENTRY_VISTA_64BIT},
      FORMAT_TYPE_7: {
          _CACHED_ENTRY_7_32BIT_SIZE: _CACHED_ENTRY_7_32BIT,
          _CACHED_ENTRY_7_64BIT_SIZE: _CACHED_ENTRY_7_64BIT},
  }

  # AppCompatCache format used in Windows 8.0.
  _CACHED_ENTRY_SIGNATURE_8_0 = u'00ts'

  # AppCompatCache format used in Windows 8.1.
  _CACHED_ENTRY_SIGNATURE_8_1 = u'10ts'

  def __init__(self, debug=False, output_writer=None):
    """Initializes an Application Compatibility Cache parser.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(AppCompatCacheDataParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

  def CheckSignature(self, value_data):
    """Parses the signature.

    Args:
      value_data (bytes): value data.

    Returns:
      int: format type or None.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    try:
      signature = self._UINT32LE.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

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

    elif format_type is not None:
      return format_type

    return

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
    header_struct = self._HEADERS.get(format_type, None)
    if not header_struct:
      raise errors.ParseError(u'Unsupported format type: {0:d}'.format(
          format_type))

    try:
      header = header_struct.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    header_data_size = self._HEADER_SIZES.get(format_type, None)
    if format_type == self.FORMAT_TYPE_10:
      header_data_size = header.signature

    if self._debug:
      self._output_writer.WriteDebugData(
          u'Header data:', value_data[0:header_data_size])

    cache_header = AppCompatCacheHeader()
    cache_header.header_size = header_data_size

    if self._debug:
      if format_type == self.FORMAT_TYPE_10:
        self._output_writer.WriteIntegerValueAsDecimal(
            u'Header size', header.signature)
      else:
        value_string = u'0x{0:08x}'.format(header.signature)
        self._output_writer.WriteValue(u'Signature', value_string)

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_10):
      cache_header.number_of_cached_entries = header.number_of_cached_entries

      if self._debug:
        self._output_writer.WriteIntegerValueAsDecimal(
            u'Number of cached entries', cache_header.number_of_cached_entries)

    if format_type == self.FORMAT_TYPE_XP:
      number_of_lru_entries = header.number_of_lru_entries
      if self._debug:
        value_string = u'0x{0:08x}'.format(number_of_lru_entries)
        self._output_writer.WriteValue(u'Number of LRU entries', value_string)

        value_string = u'0x{0:08x}'.format(header.unknown1)
        self._output_writer.WriteValue(u'Unknown1', value_string)

        self._output_writer.WriteText(u'LRU entries:')

      data_offset = 16
      if number_of_lru_entries > 0 and number_of_lru_entries <= 96:
        for lru_entry_index in range(number_of_lru_entries):
          try:
            lru_entry = self._UINT32LE.MapByteStream(
                value_data[data_offset:data_offset + 4])
          except (
              dtfabric_errors.ByteStreamTooSmallError,
              dtfabric_errors.MappingError) as exception:
            raise errors.ParseError(exception)

          data_offset += 4

          if self._debug:
            value_string = u'{0:d} (offset: 0x{1:08x})'.format(
                lru_entry, 400 + (lru_entry * 552))
            self._output_writer.WriteValue(
                u'LRU entry: {0:d}'.format(lru_entry_index), value_string)

        if self._debug:
          self._output_writer.WriteText(u'')

      if self._debug:
        self._output_writer.WriteDebugData(
            u'Unknown data:', value_data[data_offset:400])

    elif format_type == self.FORMAT_TYPE_8:
      if self._debug:
        value_string = u'0x{0:08x}'.format(header.unknown1)
        self._output_writer.WriteValue(u'Unknown1', value_string)

    if self._debug:
      self._output_writer.WriteText(u'')

    return cache_header

  def DetermineCachedEntrySize(
      self, format_type, value_data, cached_entry_offset):
    """Determines the size of a cached entry.

    Args:
      format_type (int): format type.
      value_data (bytess): value data.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.

    Returns:
      int: cached entry size or None.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if format_type not in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      raise errors.ParseError(u'Unsupported format type: {0:d}'.format(
          format_type))

    cached_entry_data = value_data[cached_entry_offset:]
    cached_entry_size = 0

    if format_type == self.FORMAT_TYPE_XP:
      cached_entry_size = self._CACHED_ENTRY_XP_32BIT_SIZE

    elif format_type in (
        self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA, self.FORMAT_TYPE_7):
      try:
        cached_entry = self._CACHED_ENTRY_2003_COMMON.MapByteStream(
            cached_entry_data)
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      if cached_entry.maximum_path_size < cached_entry.path_size:
        errors.ParseError(u'Path size value out of bounds.')
        return

      path_end_of_string_size = (
          cached_entry.maximum_path_size - cached_entry.path_size)
      if cached_entry.path_size == 0 or path_end_of_string_size != 2:
        errors.ParseError(u'Unsupported path size values.')
        return

      # Assume the entry is 64-bit if the 32-bit path offset is 0 and
      # the 64-bit path offset is set.
      if (cached_entry.path_offset_32bit == 0 and
          cached_entry.path_offset_64bit != 0):
        if format_type == self.FORMAT_TYPE_2003:
          cached_entry_size = self._CACHED_ENTRY_2003_64BIT_SIZE
        elif format_type == self.FORMAT_TYPE_VISTA:
          cached_entry_size = self._CACHED_ENTRY_VISTA_64BIT_SIZE
        elif format_type == self.FORMAT_TYPE_7:
          cached_entry_size = self._CACHED_ENTRY_7_64BIT_SIZE

      else:
        if format_type == self.FORMAT_TYPE_2003:
          cached_entry_size = self._CACHED_ENTRY_2003_32BIT_SIZE
        elif format_type == self.FORMAT_TYPE_VISTA:
          cached_entry_size = self._CACHED_ENTRY_VISTA_32BIT_SIZE
        elif format_type == self.FORMAT_TYPE_7:
          cached_entry_size = self._CACHED_ENTRY_7_32BIT_SIZE

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      cached_entry_size = self._CACHED_ENTRY_HEADER_8_SIZE

    return cached_entry_size

  def ParseCachedEntry(
      self, format_type, value_data, cached_entry_index, cached_entry_offset,
      cached_entry_size):
    """Parses a cached entry.

    Args:
      format_type (int): format type.
      value_data (bytess): value data.
      cached_entry_index (int): cached entry index.
      cached_entry_offset (int): offset of the first cached entry data
          relative to the start of the value data.
      cached_entry_size (int): cached entry data size.

    Returns:
      AppCompatCacheCachedEntry: cached entry.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if format_type not in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7, self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      raise errors.ParseError(u'Unsupported format type: {0:d}'.format(
          format_type))

    cached_entry_data = value_data[
        cached_entry_offset:cached_entry_offset + cached_entry_size]

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7):
      if self._debug:
        description = u'Cached entry: {0:d} data:'.format(cached_entry_index)
        self._output_writer.WriteDebugData(description, cached_entry_data)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      if self._debug:
        description = u'Cached entry: {0:d} header data:'.format(
            cached_entry_index)
        self._output_writer.WriteDebugData(description, cached_entry_data[:-2])

    cached_entry = None

    cached_entry_struct = self._CACHED_ENTRIES.get(format_type, {}).get(
        cached_entry_size, None)

    if cached_entry_struct:
      try:
        cached_entry = cached_entry_struct.MapByteStream(cached_entry_data)
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

    if format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      if cached_entry_data[0:4] not in (
          self._CACHED_ENTRY_SIGNATURE_8_0, self._CACHED_ENTRY_SIGNATURE_8_1):
        raise errors.ParseError(u'Unsupported cache entry signature')

      if cached_entry_size == self._CACHED_ENTRY_HEADER_8_SIZE:
        try:
          cached_entry = self._CACHED_ENTRY_HEADER_8.MapByteStream(
              cached_entry_data)
        except (
            dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError) as exception:
          raise errors.ParseError(exception)

        cached_entry_data_size = cached_entry.cached_entry_data_size
        cached_entry_size = 12 + cached_entry_data_size

        cached_entry_data = value_data[
            cached_entry_offset:cached_entry_offset + cached_entry_size]

    if not cached_entry:
      raise errors.ParseError(u'Unsupported cache entry size: {0:d}'.format(
          cached_entry_size))

    if format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      if self._debug:
        description = u'Cached entry: {0:d} data:'.format(cached_entry_index)
        self._output_writer.WriteDebugData(description, cached_entry_data)

    cached_entry_object = AppCompatCacheCachedEntry()
    cached_entry_object.cached_entry_size = cached_entry_size

    path_offset = 0
    data_size = 0

    if format_type == self.FORMAT_TYPE_XP:
      string_size = 0
      for string_index in xrange(0, 528, 2):
        if (ord(cached_entry_data[string_index]) == 0 and
            ord(cached_entry_data[string_index + 1]) == 0):
          break
        string_size += 2

      cached_entry_object.path = cached_entry_data[0:string_size].decode(
          u'utf-16-le')

      if self._debug:
        self._output_writer.WriteValue(u'Path', cached_entry_object.path)

    elif format_type in (
        self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA, self.FORMAT_TYPE_7):
      path_size = cached_entry.path_size
      maximum_path_size = cached_entry.maximum_path_size
      path_offset = cached_entry.path_offset

      if self._debug:
        self._output_writer.WriteIntegerValueAsDecimal(u'Path size', path_size)

        self._output_writer.WriteIntegerValueAsDecimal(
            u'Maximum path size', maximum_path_size)

        value_string = u'0x{0:08x}'.format(path_offset)
        self._output_writer.WriteValue(u'Path offset', value_string)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      path_size = cached_entry.path_size

      if self._debug:
        self._output_writer.WriteValue(u'Signature', cached_entry_data[0:4])

        value_string = u'0x{0:08x}'.format(cached_entry.unknown1)
        self._output_writer.WriteValue(u'Unknown1', value_string)

        self._output_writer.WriteIntegerValueAsDecimal(
            u'Cached entry data size', cached_entry_data_size)

        self._output_writer.WriteIntegerValueAsDecimal(u'Path size', path_size)

      cached_entry_data_offset = 14 + path_size
      cached_entry_object.path = cached_entry_data[
          14:cached_entry_data_offset].decode(u'utf-16-le')

      if self._debug:
        self._output_writer.WriteValue(u'Path', cached_entry_object.path)

      if format_type == self.FORMAT_TYPE_8:
        remaining_data = cached_entry_data[cached_entry_data_offset:]

        try:
          cached_entry_object.insertion_flags = self._UINT32LE.MapByteStream(
              remaining_data[0:4])
          cached_entry_object.shim_flags = self._UINT32LE.MapByteStream(
              remaining_data[4:8])
        except (
            dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError) as exception:
          raise errors.ParseError(exception)

        if self._debug:
          value_string = u'0x{0:08x}'.format(
              cached_entry_object.insertion_flags)
          self._output_writer.WriteValue(u'Insertion flags', value_string)

          value_string = u'0x{0:08x}'.format(cached_entry_object.shim_flags)
          self._output_writer.WriteValue(u'Shim flags', value_string)

        if cached_entry_data[0:4] == self._CACHED_ENTRY_SIGNATURE_8_0:
          cached_entry_data_offset += 8

        elif cached_entry_data[0:4] == self._CACHED_ENTRY_SIGNATURE_8_1:
          if self._debug:
            try:
              unknown1 = self._UINT16LE.MapByteStream(remaining_data[8:10])
            except (
                dtfabric_errors.ByteStreamTooSmallError,
                dtfabric_errors.MappingError) as exception:
              raise errors.ParseError(exception)

            value_string = u'0x{0:04x}'.format(unknown1)
            self._output_writer.WriteValue(u'Unknown1', value_string)

          cached_entry_data_offset += 10

      remaining_data = cached_entry_data[cached_entry_data_offset:]

    if format_type in (
        self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003, self.FORMAT_TYPE_VISTA,
        self.FORMAT_TYPE_7):
      cached_entry_object.last_modification_time = (
          cached_entry.last_modification_time)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      try:
        cached_entry_object.last_modification_time = (
            self._UINT64LE.MapByteStream(remaining_data[0:8]))
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

    if not cached_entry_object.last_modification_time:
      if self._debug:
        value_string = u'0x{0:08x}'.format(
            cached_entry_object.last_modification_time)
        self._output_writer.WriteValue(u'Last modification time', value_string)

    else:
      timestamp = cached_entry_object.last_modification_time // 10
      date_string = (datetime.datetime(1601, 1, 1) +
                     datetime.timedelta(microseconds=timestamp))

      if self._debug:
        value_string = u'{0!s} (0x{1:08x})'.format(
            date_string, cached_entry_object.last_modification_time)
        self._output_writer.WriteValue(u'Last modification time', value_string)

    if format_type in (self.FORMAT_TYPE_XP, self.FORMAT_TYPE_2003):
      cached_entry_object.file_size = cached_entry.file_size

      if self._debug:
        self._output_writer.WriteIntegerValueAsDecimal(
            u'File size', cached_entry_object.file_size)

    elif format_type in (self.FORMAT_TYPE_VISTA, self.FORMAT_TYPE_7):
      cached_entry_object.insertion_flags = cached_entry.insertion_flags
      cached_entry_object.shim_flags = cached_entry.shim_flags

      if self._debug:
        value_string = u'0x{0:08x}'.format(cached_entry_object.insertion_flags)
        self._output_writer.WriteValue(u'Insertion flags', value_string)

        value_string = u'0x{0:08x}'.format(cached_entry_object.shim_flags)
        self._output_writer.WriteValue(u'Shim flags', value_string)

    if format_type == self.FORMAT_TYPE_XP:
      cached_entry_object.last_update_time = cached_entry.last_update_time

      if not cached_entry_object.last_update_time:
        if self._debug:
          value_string = u'0x{0:08x}'.format(
              cached_entry_object.last_update_time)
          self._output_writer.WriteValue(u'Last update time', value_string)

      else:
        timestamp = cached_entry_object.last_update_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        if self._debug:
          value_string = u'{0!s} (0x{1:08x})'.format(
              date_string, cached_entry_object.last_update_time)
          self._output_writer.WriteValue(u'Last update time', value_string)

    if format_type == self.FORMAT_TYPE_7:
      data_offset = cached_entry.data_offset
      data_size = cached_entry.data_size

      if self._debug:
        value_string = u'0x{0:08x}'.format(data_offset)
        self._output_writer.WriteValue(u'Data offset', value_string)

        self._output_writer.WriteIntegerValueAsDecimal(u'Data size', data_size)

    elif format_type in (self.FORMAT_TYPE_8, self.FORMAT_TYPE_10):
      data_offset = cached_entry_offset + cached_entry_data_offset + 12

      try:
        data_size = self._UINT32LE.MapByteStream(remaining_data[8:12])
      except (
          dtfabric_errors.ByteStreamTooSmallError,
          dtfabric_errors.MappingError) as exception:
        raise errors.ParseError(exception)

      if self._debug:
        self._output_writer.WriteIntegerValueAsDecimal(u'Data size', data_size)

    if self._debug:
      self._output_writer.WriteText(u'')

    if path_offset > 0 and path_size > 0:
      path_size += path_offset
      maximum_path_size += path_offset

      if self._debug:
        self._output_writer.WriteDebugData(
            u'Path data:', value_data[path_offset:maximum_path_size])

      cached_entry_object.path = value_data[path_offset:path_size].decode(
          u'utf-16-le')

      if self._debug:
        self._output_writer.WriteValue(u'Path', cached_entry_object.path)
        self._output_writer.WriteText(u'')

    if data_size > 0:
      data_size += data_offset

      cached_entry_object.data = value_data[data_offset:data_size]

      if self._debug:
        self._output_writer.WriteDebugData(u'Data:', cached_entry_object.data)

    return cached_entry_object


class AppCompatCacheCollector(interface.WindowsRegistryKeyCollector):
  """Application Compatibility Cache collector."""

  def _CollectAppCompatCacheFromKey(self, app_compat_cache_key, output_writer):
    """Collects Application Compatibility Cache from a Windows Registry key.

    Args:
      app_compat_cache_key (dfwinreg.WinRegistryKey): Application Compatibility
          Cache Windows Registry key.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Application Compatibility Cache key was found,
          False if not.
    """
    value = app_compat_cache_key.GetValueByName(u'AppCompatCache')
    if not value:
      logging.warning(u'Missing AppCompatCache value in key: {0:s}'.format(
          app_compat_cache_key.path))
      return True

    value_data = value.data
    value_data_size = len(value.data)

    # TODO: add non debug output
    parser = AppCompatCacheDataParser(
        debug=self._debug, output_writer=output_writer)

    if self._debug:
      output_writer.WriteDebugData(u'Value data:', value_data)

    format_type = parser.CheckSignature(value_data)
    if not format_type:
      logging.warning(u'Unsupported signature.')
      return True

    cache_header = parser.ParseHeader(format_type, value_data)

    # On Windows Vista and 2008 when the cache is empty it will
    # only consist of the header.
    if value_data_size <= cache_header.header_size:
      return True

    cached_entry_offset = cache_header.header_size
    cached_entry_size = parser.DetermineCachedEntrySize(
        format_type, value_data, cached_entry_offset)

    if not cached_entry_size:
      logging.warning(u'Unsupported cached entry size.')
      return True

    cached_entry_index = 0
    while cached_entry_offset < value_data_size:
      cached_entry = parser.ParseCachedEntry(
          format_type, value_data, cached_entry_index, cached_entry_offset,
          cached_entry_size)

      output_writer.WriteCachedEntry(cached_entry)

      cached_entry_offset += cached_entry.cached_entry_size
      cached_entry_index += 1

      if (cache_header.number_of_cached_entries != 0 and
          cached_entry_index >= cache_header.number_of_cached_entries):
        break

    return True

  def Collect(self, registry, output_writer, all_control_sets=False):
    """Collects the Application Compatibility Cache.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.
      all_control_sets (Optional[bool]): True if the services should be
          collected from all control sets instead of only the current control
          set.

    Returns:
      bool: True if the Application Compatibility Cache key was found,
          False if not.
    """
    result = False

    if all_control_sets:
      system_key = registry.GetKeyByPath(u'HKEY_LOCAL_MACHINE\\System\\')
      if not system_key:
        return result

      for control_set_key in system_key.GetSubkeys():
        if control_set_key.name.startswith(u'ControlSet'):
          # Windows XP
          app_compat_cache_key = control_set_key.GetSubkeyByPath(
              u'Control\\Session Manager\\AppCompatibility')
          if app_compat_cache_key:
            if self._CollectAppCompatCacheFromKey(
                app_compat_cache_key, output_writer):
              result = True

          # Windows 2003 and later
          app_compat_cache_key = control_set_key.GetSubkeyByPath(
              u'Control\\Session Manager\\AppCompatCache')
          if app_compat_cache_key:
            if self._CollectAppCompatCacheFromKey(
                app_compat_cache_key, output_writer):
              result = True

    else:
      # Windows XP
      key_path = (
          u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\'
          u'Session Manager\\AppCompatibility')
      app_compat_cache_key = registry.GetKeyByPath(key_path)
      if app_compat_cache_key:
        if self._CollectAppCompatCacheFromKey(
            app_compat_cache_key, output_writer):
          result = True

      # Windows 2003 and later
      key_path = (
          u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\'
          u'Session Manager\\AppCompatCache')
      app_compat_cache_key = registry.GetKeyByPath(key_path)
      if app_compat_cache_key:
        if self._CollectAppCompatCacheFromKey(
            app_compat_cache_key, output_writer):
          result = True

    return result
