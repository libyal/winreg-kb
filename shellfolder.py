#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Script to print the shell folder class identifiers
# from the SOFTWARE Registry file (REGF)
#
# Copyright (c) 2013, Joachim Metz <joachim.metz@gmail.com>
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
import sys

import pyregf


class StdoutWriter(object):
  def Write(self, guid, name, localized_string):
      print "{0:s}\t{1:s}\t{2:s}".format(guid, name, localized_string)


def Main():
  args_parser = argparse.ArgumentParser(description=(
      "Extract the shell folder class identifiers from a SOFTWARE "
      " Registry File (REGF)."))

  args_parser.add_argument(
      'registry_file', nargs='?', action='store', metavar='SOFTWARE',
      default=None, help='The path of the SOFTWARE Registry file.')

  options = args_parser.parse_args()

  if not options.registry_file:
    print 'Registry file missing.'
    print ''
    args_parser.print_help()
    print ''
    return False

  writer = StdoutWriter()

  class_identifiers_key_path = "Classes\\CLSID"

  regf_file = pyregf.file()
  regf_file.open(options.registry_file)

  class_identifiers_key = regf_file.get_key_by_path(class_identifiers_key_path)

  if class_identifiers_key:
    for class_identifier_key in class_identifiers_key.sub_keys:
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.get_sub_key_by_name("ShellFolder")
      if shell_folder_key:
        value = class_identifier_key.get_value_by_name("")
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode("utf-16-le")[:-1]
        else:
          name = ""

        value = class_identifier_key.get_value_by_name("LocalizedString")
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode("utf-16-le")[:-1]
        else:
          localized_string = ""

        writer.Write(guid, name, localized_string)
  else:
    print "No class identifiers key found."

  regf_file.close()

  return True

if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
