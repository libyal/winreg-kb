#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import sys

import pyregf


class StdoutWriter(object):
  def Open(self):
    return True

  def Close(self):
    return True

  def Write(self, guid, name, localized_name):
    print u'{0:s}\t{1:s}\t{2:s}'.format(guid, name, localized_name)


def Main():
  args_parser = argparse.ArgumentParser(description=(
      'Extract the known folder identifiers (KNOWNFOLDERID) from a SOFTWARE '
      'Registry File (REGF).'))

  args_parser.add_argument(
      'registry_file', nargs='?', action='store', metavar='SOFTWARE',
      default=None, help='path of the SOFTWARE Registry file.')

  options = args_parser.parse_args()

  if not options.registry_file:
    print u'Registry file missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  writer = StdoutWriter()

  writer.Open()

  regf_file = pyregf.file()
  regf_file.open(options.registry_file)

  folder_descriptions_key_path = (
      'Microsoft\\Windows\\CurrentVersion\\Explorer\\FolderDescriptions')

  folder_descriptions_key = regf_file.get_key_by_path(
      folder_descriptions_key_path)

  if folder_descriptions_key:
    for known_folder_key in folder_descriptions_key.sub_keys:
      guid = known_folder_key.name.lower()

      value = known_folder_key.get_value_by_name('Name')
      if value:
        name = value.get_data_as_string()
      else:
        name = ''

      value = known_folder_key.get_value_by_name('LocalizedName')
      if value:
        localized_name = value.get_data_as_string()
      else:
        localized_name = ''

      writer.Write(guid, name, localized_name)
  else:
    print u'No folder descriptions key found.'

  regf_file.close()

  writer.Close()

  return True

if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
