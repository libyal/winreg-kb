#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the AppCompatCache information in the Windows Registry
# from the SYSTEM Registry file (REGF)
#
# Copyright (c) 2014, Joachim Metz <joachim.metz@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import construct
import datetime
import logging
import sys

import pyregf


HEXDUMP_CHARACTER_MAP = [
    '.' if byte < 0x20 or byte > 0x7e else chr(byte) for byte in range(256)]


def Hexdump(data):
    lines = []
    for block_index in xrange(0, len(data), 16):
        data_string = data[block_index:block_index+16]

        hexadecimal_string1 = ' '.join([
            '{0:02x}'.format(ord(byte)) for byte in data_string[0:8]])
        hexadecimal_string2 = ' '.join([
            '{0:02x}'.format(ord(byte)) for byte in data_string[8:16]])

        printable_string = ''.join([
            HEXDUMP_CHARACTER_MAP[ord(byte)] for byte in data_string])

        whitespace = ' ' * ((3 * (16 - len(data_string))) - 1)

        lines.append('0x{0:08x}  {1:s}  {2:s}{3:s}  {4:s}\n'.format(
            block_index, hexadecimal_string1, hexadecimal_string2,
            whitespace, printable_string))

    return ''.join(lines)


def PrintAppCompatCacheKey(regf_file, appcompatcache_key_path):

  APPCOMPATCACHE_FORMAT_TYPE_2000 = 1
  APPCOMPATCACHE_FORMAT_TYPE_XP = 2
  APPCOMPATCACHE_FORMAT_TYPE_2003 = 3
  APPCOMPATCACHE_FORMAT_TYPE_VISTA = 4
  APPCOMPATCACHE_FORMAT_TYPE_7 = 5
  APPCOMPATCACHE_FORMAT_TYPE_8 = 6
  APPCOMPATCACHE_FORMAT_TYPE_8_1 = 7

  # AppCompatCache format signature used in Windows XP.
  APPCOMPATCACHE_HEADER_SIGNATURE_XP = 0xdeadbeef

  # AppCompatCache format used in Windows XP.
  APPCOMPATCACHE_HEADER_XP_STRUCT = construct.Struct(
      'appcompatcache_header_xp',
      construct.ULInt32('signature'),
      construct.ULInt32('number_of_cached_entries'),
      construct.ULInt32('number_of_characters'),
      construct.ULInt32('unknown1'))

  # AppCompatCache format signature used in Windows 2003, Vista and 2008.
  APPCOMPATCACHE_HEADER_SIGNATURE_2003 = 0xbadc0ffe

  # AppCompatCache format used in Windows 2003.
  APPCOMPATCACHE_HEADER_2003_STRUCT = construct.Struct(
      'appcompatcache_header_2003',
      construct.ULInt32('signature'),
      construct.ULInt32('number_of_cached_entries'),
      construct.Padding(120))
  # TODO: unsure about padding.

  APPCOMPATCACHE_CACHE_ENTRY_2003_32BIT_STRUCT = construct.Struct(
      'appcompatcache_cache_entry_2003_32bit',
      construct.ULInt16('path_size'),
      construct.ULInt16('maximum_path_size'),
      construct.ULInt32('path_offset'),
      construct.ULInt64('last_modification_time'),
      construct.ULInt64('file_size'))

  APPCOMPATCACHE_CACHE_ENTRY_2003_64BIT_STRUCT = construct.Struct(
      'appcompatcache_cache_entry_2003_64bit',
      construct.ULInt16('path_size'),
      construct.ULInt16('maximum_path_size'),
      construct.ULInt32('unknown1'),
      construct.ULInt64('path_offset'),
      construct.ULInt64('last_modification_time'),
      construct.ULInt64('file_size'))

  # AppCompatCache format used in Windows Vista and 2008.

  # AppCompatCache format signature used in Windows 7 and 2008 R2.
  APPCOMPATCACHE_HEADER_SIGNATURE_7 = 0xbadc0fee

  # AppCompatCache format used in Windows 7 and 2008 R2.
  APPCOMPATCACHE_HEADER_7_STRUCT = construct.Struct(
      'appcompatcache_header_7',
      construct.ULInt32('signature'),
      construct.ULInt32('number_of_cached_entries'),
      construct.Padding(120))

  APPCOMPATCACHE_CACHE_ENTRY_7_32BIT_STRUCT = construct.Struct(
      'appcompatcache_cache_entry_7_32bit',
      construct.ULInt16('path_size'),
      construct.ULInt16('maximum_path_size'),
      construct.ULInt32('path_offset'),
      construct.ULInt64('last_modification_time'),
      construct.ULInt32('insertion_flags'),
      construct.ULInt32('shim_flags'),
      construct.ULInt32('data_size'),
      construct.ULInt32('data_offset'))

  APPCOMPATCACHE_CACHE_ENTRY_7_64BIT_STRUCT = construct.Struct(
      'appcompatcache_cache_entry_7_64bit',
      construct.ULInt16('path_size'),
      construct.ULInt16('maximum_path_size'),
      construct.ULInt32('unknown1'),
      construct.ULInt64('path_offset'),
      construct.ULInt64('last_modification_time'),
      construct.ULInt32('insertion_flags'),
      construct.ULInt32('shim_flags'),
      construct.ULInt64('data_size'),
      construct.ULInt64('data_offset'))

  # AppCompatCache format used in Windows 8.0.

  # AppCompatCache format used in Windows 8.1.

  appcompatibility_key = regf_file.get_key_by_path(appcompatcache_key_path)
  if not appcompatibility_key:
    return

  value = appcompatibility_key.get_value_by_name('AppCompatCache')
  if not value:
    logging.warning(u'Missing AppCompatCache value in key: {0:s}'.format(
        appcompatcache_key_path))
    return

  value_data = value.data
  value_data_index = 0

  signature = construct.ULInt32('signature').parse(value_data)

  if signature == APPCOMPATCACHE_HEADER_SIGNATURE_XP:
    format_type = APPCOMPATCACHE_FORMAT_TYPE_XP

    header_size = APPCOMPATCACHE_HEADER_XP_STRUCT.sizeof()
    parsed_data = APPCOMPATCACHE_HEADER_XP_STRUCT.parse(value_data)

  elif signature == APPCOMPATCACHE_HEADER_SIGNATURE_2003:
    format_type = APPCOMPATCACHE_FORMAT_TYPE_2003

    # TODO: determine which format version is used.
    header_size = APPCOMPATCACHE_HEADER_2003_STRUCT.sizeof()
    parsed_data = APPCOMPATCACHE_HEADER_2003_STRUCT.parse(value_data)

    # TODO: determine bit size.
    bit_size = 32

  elif signature == APPCOMPATCACHE_HEADER_SIGNATURE_7:
    format_type = APPCOMPATCACHE_FORMAT_TYPE_7

    # TODO: determine which format version is used.
    header_size = APPCOMPATCACHE_HEADER_7_STRUCT.sizeof()
    parsed_data = APPCOMPATCACHE_HEADER_7_STRUCT.parse(value_data)

    # TODO: determine bit size.
    bit_size = 64

  else:
    logging.warning(u'Unsupported signature: 0x{0:08x}'.format(signature))

    print u'Value data:'
    print Hexdump(value_data)
    return

  next_value_data_index = value_data_index + header_size

  print u'Header data:'
  print Hexdump(value_data[value_data_index:next_value_data_index])

  value_data_index = next_value_data_index

  number_of_cached_entries = parsed_data.get('number_of_cached_entries')

  print u'Signature\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(signature)
  print u'Number of cached entries\t\t\t\t\t\t: {0:d}'.format(
      number_of_cached_entries)

  if format_type == APPCOMPATCACHE_FORMAT_TYPE_XP:
    number_of_characters = parsed_data.get('number_of_characters')

    number_of_entries *= 4
    number_of_entries += 16

    print u'Number of characters\t\t\t\t\t\t\t: {0:d}'.format(
        number_of_characters)

    print u'Unknown1\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
        parsed_data.get('unknown1'))

  print u''

  if format_type == APPCOMPATCACHE_FORMAT_TYPE_XP:
    number_of_characters *= 2
    number_of_characters += number_of_entries

    # TODO: likely header data?
    print u'Cached entry array data:'
    print Hexdump(value_data[16:number_of_entries])

    print u'String array data:'
    print Hexdump(value_data[number_of_entries:number_of_characters])

  if format_type == APPCOMPATCACHE_FORMAT_TYPE_XP:
    pass

  elif format_type == APPCOMPATCACHE_FORMAT_TYPE_2003:
    if bit_size == 32:
      cached_entry_size = APPCOMPATCACHE_CACHE_ENTRY_2003_32BIT_STRUCT.sizeof()
    elif bit_size == 64:
      cached_entry_size = APPCOMPATCACHE_CACHE_ENTRY_2003_64BIT_STRUCT.sizeof()

  elif format_type == APPCOMPATCACHE_FORMAT_TYPE_7:
    if bit_size == 32:
      cached_entry_size = APPCOMPATCACHE_CACHE_ENTRY_7_32BIT_STRUCT.sizeof()
    elif bit_size == 64:
      cached_entry_size = APPCOMPATCACHE_CACHE_ENTRY_7_64BIT_STRUCT.sizeof()

  for cached_entry_index in range(0, number_of_cached_entries):
    next_value_data_index = value_data_index + cached_entry_size

    print u'Cached entry: {0:d} data:'.format(cached_entry_index)
    print Hexdump(value_data[value_data_index:next_value_data_index])

    if format_type == APPCOMPATCACHE_FORMAT_TYPE_XP:
      # TODO: implement.
      pass

    elif format_type == APPCOMPATCACHE_FORMAT_TYPE_2003:
      if bit_size == 32:
        parsed_data = APPCOMPATCACHE_CACHE_ENTRY_2003_32BIT_STRUCT.parse(
          value_data[value_data_index:])
      elif bit_size == 64:
        parsed_data = APPCOMPATCACHE_CACHE_ENTRY_2003_64BIT_STRUCT.parse(
            value_data[value_data_index:])

    elif format_type == APPCOMPATCACHE_FORMAT_TYPE_7:
      if bit_size == 32:
        parsed_data = APPCOMPATCACHE_CACHE_ENTRY_7_32BIT_STRUCT.parse(
            value_data[value_data_index:])
      elif bit_size == 64:
        parsed_data = APPCOMPATCACHE_CACHE_ENTRY_7_64BIT_STRUCT.parse(
            value_data[value_data_index:])

    path_size = parsed_data.get('path_size')
    maximum_path_size = parsed_data.get('maximum_path_size')
    path_offset = parsed_data.get('path_offset')

    print u'Path size\t\t\t\t\t\t\t\t: {0:d}'.format(path_size)
    print u'Maximum path size\t\t\t\t\t\t\t: {0:d}'.format(maximum_path_size)
    print u'Path offset\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(path_offset)

    timestamp = parsed_data.get('last_modification_time')
    date_string = (datetime.datetime(1601, 1, 1) +
                   datetime.timedelta(microseconds=timestamp/10))

    print u'Last modification time\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
        date_string, timestamp)

    if format_type == APPCOMPATCACHE_FORMAT_TYPE_XP:
      data_size = 0

    elif format_type == APPCOMPATCACHE_FORMAT_TYPE_2003:
      data_size = 0

    elif format_type == APPCOMPATCACHE_FORMAT_TYPE_7:
      data_offset = parsed_data.get('data_offset')
      data_size = parsed_data.get('data_size')

      print u'Insertion flags\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
          parsed_data.get('insertion_flags'))
      print u'Shim flags\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
          parsed_data.get('shim_flags'))
      print u'Data offset\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(data_offset)
      print u'Data size\t\t\t\t\t\t\t\t: {0:d}'.format(data_size)

    path_size += path_offset
    maximum_path_size += path_offset

    print u''
    print u'Path data:'
    print Hexdump(value_data[path_offset:maximum_path_size])

    print u'Path\t\t\t\t\t\t\t\t\t: {0:s}'.format(
        value_data[path_offset:path_size].decode('utf-16-le'))

    if data_size > 0:
      data_size += data_offset

      print u'Data:'
      print Hexdump(value_data[data_offset:data_size])

    value_data_index = next_value_data_index

  print u''


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the MSIE zone information from a SYSTEM '
      'Registry File (REGF).'))

  args_parser.add_argument(
      'registry_file', nargs='?', action='store', metavar='SYSTEM',
      default=None, help='path of the SYSTEM Registry file.')

  options = args_parser.parse_args()

  if not options.registry_file:
    print u'Registry file missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  regf_file = pyregf.file()
  regf_file.open(options.registry_file)

  # HKLM

  # Windows XP
  PrintAppCompatCacheKey(
   regf_file,
   'ControlSet001\Control\Session Manager\AppCompatibility')

  # Windows 2003 and later
  PrintAppCompatCacheKey(
   regf_file,
   'ControlSet001\Control\Session Manager\AppCompatCache')

  # TODO: handle multiple control sets.

  regf_file.close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

