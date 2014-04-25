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
  # AppCompatCache format used in Windows XP.
  APPCOMPATCACHE_HEADER_SIGNATURE_XP = 0xdeadbeef
  APPCOMPATCACHE_HEADER_XP_32BIT_STRUCT = construct.Struct(
      'appcompatcache_header_xp_32bit',
      construct.ULInt32('signature'),
      construct.ULInt32('number_of_entries'),
      construct.ULInt32('number_of_characters'),
      construct.ULInt32('unknown1'))

  # AppCompatCache format used in Windows 2003, 7 and 2008.
  APPCOMPATCACHE_HEADER_SIGNATURE_2003 = 0xbadc0ffe
  APPCOMPATCACHE_HEADER_2003_32BIT_STRUCT = construct.Struct(
      'appcompatcache_header_2003_32bit',
      construct.ULInt32('signature'),
      construct.ULInt32('number_of_entries'),
      construct.ULInt32('number_of_characters'),
      construct.ULInt32('unknown1'))

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

  print u'Header data:'
  print Hexdump(value_data[0:16])

  parsed_data = APPCOMPATCACHE_HEADER_XP_32BIT_STRUCT.parse(value_data)

  signature = parsed_data.get('signature')
  number_of_entries = parsed_data.get('number_of_entries')
  number_of_characters = parsed_data.get('number_of_characters')

  print u'Signature\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(signature)
  print u'Number of entries\t\t\t\t\t\t\t: {0:d}'.format(number_of_entries)
  print u'Number of characters\t\t\t\t\t\t\t: {0:d}'.format(
      number_of_characters)

  print u'Unknown1\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
      parsed_data.get('unknown1'))

  if signature not in [
      APPCOMPATCACHE_HEADER_SIGNATURE_XP,
      APPCOMPATCACHE_HEADER_SIGNATURE_2003]:
    logging.warning(u'Unsupported signature: 0x{0:08x}'.format(signature))
    return

  number_of_entries *= 4
  number_of_entries += 16

  number_of_characters *= 2
  number_of_characters += number_of_entries

  print u'Integer array data:'
  print Hexdump(value_data[16:number_of_entries])

  print u'String array data:'
  print Hexdump(value_data[number_of_entries:number_of_characters])

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

