#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import datetime
import construct
import logging
import sys

import pyregf

import hexdump


# pylint: disable=logging-format-interpolation

def PrintUserAssistKey(regf_file, userassist_key_path, unused_ascii_codepage):
  # UserAssist format version used in Windows 2000, XP, 2003, Vista.
  USERASSIST_V3_STRUCT = construct.Struct(
      'userassist_entry',
      construct.ULInt32('unknown1'),
      construct.ULInt32('execution_count'),
      construct.ULInt64('last_execution_time'))

  # UserAssist format version used in Windows 2008, 7, 8.
  USERASSIST_V5_STRUCT = construct.Struct(
      'userassist_entry',
      construct.ULInt32('unknown1'),
      construct.ULInt32('execution_count'),
      construct.ULInt32('application_focus_count'),
      construct.ULInt32('application_focus_duration'),
      construct.LFloat32('unknown2'),
      construct.LFloat32('unknown3'),
      construct.LFloat32('unknown4'),
      construct.LFloat32('unknown5'),
      construct.LFloat32('unknown6'),
      construct.LFloat32('unknown7'),
      construct.LFloat32('unknown8'),
      construct.LFloat32('unknown9'),
      construct.LFloat32('unknown10'),
      construct.LFloat32('unknown11'),
      construct.ULInt32('unknown12'),
      construct.ULInt64('last_execution_time'),
      construct.ULInt32('unknown13'))

  userassist_key = regf_file.get_key_by_path(userassist_key_path)
  if not userassist_key:
    logging.warning(u'Missing UserAssist key: {0:s}'.format(
        userassist_key_path))
    return

  print u'Key: {0:s}'.format(userassist_key_path)
  print u''

  for guid_sub_key in userassist_key.sub_keys:
    version_value = guid_sub_key.get_value_by_name('Version')

    if not version_value:
      logging.warning(u'Missing Version value in sub key: {0:s}'.format(
          guid_sub_key.name))
      continue

    format_version = version_value.data_as_integer
    if format_version == 3:
      value_data_size = USERASSIST_V3_STRUCT.sizeof()
    elif format_version == 5:
      value_data_size = USERASSIST_V5_STRUCT.sizeof()

    print u'GUID\t\t: {0:s}'.format(guid_sub_key.name)
    print u'Format version\t: {0:d}'.format(format_version)
    print u''

    count_sub_key = guid_sub_key.get_sub_key_by_name('Count')
    for value in count_sub_key.values:
      output_string = u'Original name\t: {0:s}'.format(value.name)
      print output_string.encode('utf-8')

      try:
        value_name = value.name.decode('rot-13')
      except UnicodeEncodeError as exception:
        characters = []
        for char in value.name:
          if ord(char) < 128:
            try:
              characters.append(char.decode('rot-13'))
            except UnicodeEncodeError:
              characters.append(char)
          else:
            characters.append(char)

        value_name = u''.join(characters)

      try:
        output_string = u'Converted name\t: {0:s}'.format(value_name)
        print output_string.encode('utf-8')
      except UnicodeEncodeError as exception:
        logging.warning(u'Unable to convert: {0:s} with error: {1:s}'.format(
            value.name, exception))

      print u'Value data:'
      print hexdump.Hexdump(value.data)

      if value_name != u'UEME_CTLSESSION':
        if value_data_size != len(value.data):
          logging.warning((
              u'Version: {0:d} size mismatch (calculated: {1:d}, '
              u'stored: {2:d}).').format(
                  format_version, value_data_size, len(value.data)))
          continue

        if format_version == 3:
          parsed_data = USERASSIST_V3_STRUCT.parse(value.data)
        elif format_version == 5:
          parsed_data = USERASSIST_V5_STRUCT.parse(value.data)

        print u'Unknown1\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            parsed_data.get('unknown1'))

        print u'Execution count\t\t\t\t\t\t\t\t: {0:d}'.format(
            parsed_data.get('execution_count'))

        if format_version == 5:
          print u'Application focus count\t\t\t\t\t\t\t: {0:d}'.format(
              parsed_data.get('application_focus_count'))

          print u'Application focus duration\t\t\t\t\t\t: {0:d}'.format(
              parsed_data.get('application_focus_duration'))

          print u'Unknown2\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown2'))

          print u'Unknown3\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown3'))

          print u'Unknown4\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown4'))

          print u'Unknown5\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown5'))

          print u'Unknown6\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown6'))

          print u'Unknown7\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown7'))

          print u'Unknown8\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown8'))

          print u'Unknown9\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown9'))

          print u'Unknown10\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown10'))

          print u'Unknown11\t\t\t\t\t\t\t\t: {0:.2f}'.format(
              parsed_data.get('unknown11'))

          print u'Unknown12\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
              parsed_data.get('unknown12'))

        timestamp = parsed_data.get('last_execution_time')
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp/10))

        print u'Last execution time\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
            date_string, timestamp)

        if format_version == 5:
          print u'Unknown13\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
              parsed_data.get('unknown13'))

        print u''


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Extract the MSIE zone information from a NTUSER.DAT '
      'Registry File (REGF).'))

  args_parser.add_argument(
      'registry_file', nargs='?', action='store', metavar='NTUSER.DAT',
      default=None, help='path of the NTUSER.DAT Registry file.')

  args_parser.add_argument(
      '--codepage', dest='codepage', action='store', metavar='CODEPAGE',
      default='cp1252', help='the codepage of the extended ASCII strings.')

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

  # HKCU

  key_path = (
      'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\UserAssist')
  PrintUserAssistKey(regf_file, key_path, options.codepage)

  regf_file.close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
