# -*- coding: utf-8 -*-
"""Windows program cache collector."""

from __future__ import print_function
import logging
import uuid

import construct
import pyfwsi  # pylint: disable=wrong-import-order

from dfwinreg import registry

from winregrc import collector
from winregrc import hexdump


class ProgramsCacheDataParser(object):
  """Class that parses the Programs Cache value data."""

  _HEADER_STRUCT = construct.Struct(
      u'programscache_header',
      construct.ULInt32(u'format_version'))

  _HEADER_9_STRUCT = construct.Struct(
      u'programscache_header_9',
      construct.ULInt16(u'unknown2'))

  _ENTRY_HEADER_STRUCT = construct.Struct(
      u'programscache_entry_header',
      construct.ULInt32(u'data_size'))

  _ENTRY_FOOTER_STRUCT = construct.Struct(
      u'programscache_entry_footer',
      construct.Byte(u'sentinel'))

  def __init__(self, debug=False):
    """Initializes the parser object.

    Args:
      debug: optional boolean value to indicate if debug information should
             be printed.
    """
    super(ProgramsCacheDataParser, self).__init__()
    self._debug = debug

  def Parse(self, value_data, value_data_size):
    """Parses the value data.

    Args:
      value_data: a binary string containing the value data.
      value_data_size: the size of the value data.

    Returns:
      TODO

    Raises:
      RuntimeError: if the format is not supported.
    """
    header_struct = self._HEADER_STRUCT.parse(value_data)
    value_data_offset = self._HEADER_STRUCT.sizeof()

    format_version = header_struct.get(u'format_version')
    if self._debug:
      print(u'Format version\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
          format_version))

    if format_version == 0x01:
      value_data_offset += 4

    elif format_version == 0x09:
      header_struct = self._HEADER_9_STRUCT.parse(value_data)
      value_data_offset += self._HEADER_9_STRUCT.sizeof()

      if self._debug:
        print(u'Unknown2\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            header_struct.get(u'unknown2')))

    elif format_version in [0x0c, 0x13]:
      uuid_object = uuid.UUID(bytes_le=value_data[4:20])
      value_data_offset += 16

      if self._debug:
        print(u'Known folder identifier\t\t\t\t\t\t\t: {0!s}'.format(
            uuid_object))

    else:
      raise RuntimeError(u'Unsupported format.')

    if format_version == 0x09:
      sentinel = 0
    else:
      entry_footer_struct = self._ENTRY_FOOTER_STRUCT.parse(
          value_data[value_data_offset:])
      value_data_offset += self._ENTRY_FOOTER_STRUCT.sizeof()

      sentinel = entry_footer_struct.get(u'sentinel')
      if self._debug:
        print(u'Sentinel\t\t\t\t\t\t\t\t: 0x{0:02x}'.format(sentinel))

    if self._debug:
      print(u'')

    while sentinel in [0x00, 0x01]:
      entry_header_struct = self._ENTRY_HEADER_STRUCT.parse(
          value_data[value_data_offset:])
      value_data_offset += self._ENTRY_HEADER_STRUCT.sizeof()

      entry_data_size = entry_header_struct.get(u'data_size')

      if self._debug:
        print(u'Entry data offset\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            value_data_offset))
        print(u'Entry data size\t\t\t\t\t\t\t\t: {0:d}'.format(
            entry_data_size))

      shell_item_list = pyfwsi.item_list()
      shell_item_list.copy_from_byte_stream(value_data[value_data_offset:])

      for shell_item in iter(shell_item_list.items):
        if self._debug:
          print(u'Shell item: 0x{0:02x}'.format(shell_item.class_type))
          print(u'Shell item: {0:s}'.format(getattr(shell_item, u'name', u'')))

      value_data_offset += entry_data_size

      entry_footer_struct = self._ENTRY_FOOTER_STRUCT.parse(
          value_data[value_data_offset:])
      value_data_offset += self._ENTRY_FOOTER_STRUCT.sizeof()

      sentinel = entry_footer_struct.get(u'sentinel')
      if self._debug:
        print(u'Sentinel\t\t\t\t\t\t\t\t: 0x{0:02x}'.format(sentinel))
        print(u'')

      if sentinel == 0x02 and value_data_offset < value_data_size:
        # TODO: determine the logic to this value.
        while ord(value_data[value_data_offset]) != 0x00:
          value_data_offset += 1
        value_data_offset += 7

        entry_footer_struct = self._ENTRY_FOOTER_STRUCT.parse(
            value_data[value_data_offset:])
        value_data_offset += self._ENTRY_FOOTER_STRUCT.sizeof()

        sentinel = entry_footer_struct.get(u'sentinel')
        if self._debug:
          print(u'Sentinel\t\t\t\t\t\t\t\t: 0x{0:02x}'.format(sentinel))
          print(u'')

    if value_data_offset < value_data_size:
      print(u'Trailing data:')
      print(u'Trailing data offset\t\t\t\t\t\t\t: 0x{0:08x}'.format(
          value_data_offset))
      print(hexdump.Hexdump(value_data[value_data_offset:]))


class ProgramsCacheCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows program cache collector.

  Attributes:
    key_found: boolean value to indicate the Windows Registry key was found.
  """

  _STARTPAGE_KEY_PATH = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\StartPage')

  _STARTPAGE2_KEY_PATH = (
      u'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\'
      u'Explorer\\StartPage2')

  def __init__(self, debug=False, mediator=None):
    """Initializes the collector object.

    Args:
      debug: optional boolean value to indicate if debug information should
             be printed.
      mediator: a volume scanner mediator (instance of
                dfvfs.VolumeScannerMediator) or None.
    """
    super(ProgramsCacheCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  def _CollectProgramsCacheFromValue(self, output_writer, key_path, value_name):
    """Collects Programs Cache from a Windows Registry value.

    Args:
      output_writer: the output writer object.
      key_path: the path of the Programs Cache key.
      value_name: the name of the Programs Cache value.
    """
    startpage_key = self._registry.GetKeyByPath(key_path)
    if not startpage_key:
      return

    self.key_found = True
    value = startpage_key.GetValueByName(value_name)
    if not value:
      logging.warning(u'Missing {0:s} value in key: {1:s}'.format(
          value_name, key_path))
      return

    value_data = value.data
    value_data_size = len(value.data)

    parser = ProgramsCacheDataParser(debug=self._debug)

    if self._debug:
      # TODO: replace WriteText by more output specific method e.g.
      # WriteValueData.
      output_writer.WriteText(u'Value data:')
      output_writer.WriteText(hexdump.Hexdump(value_data))

    parser.Parse(value_data, value_data_size)

  def Collect(self, output_writer):
    """Collects the system information.

    Args:
      output_writer: the output writer object.
    """
    self.key_found = False

    self._CollectProgramsCacheFromValue(
        output_writer, self._STARTPAGE_KEY_PATH, u'ProgramsCache')

    self._CollectProgramsCacheFromValue(
        output_writer, self._STARTPAGE2_KEY_PATH, u'ProgramsCache')

    self._CollectProgramsCacheFromValue(
        output_writer, self._STARTPAGE2_KEY_PATH, u'ProgramsCacheSMP')

    self._CollectProgramsCacheFromValue(
        output_writer, self._STARTPAGE2_KEY_PATH, u'ProgramsCacheTBP')
