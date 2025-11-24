#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to extract a catalog of Windows Registry keys and values."""

import argparse
import logging
import re
import sys

from dfwinreg import creg as dfwinreg_creg
from dfwinreg import regf as dfwinreg_regf
from dfwinreg import registry as dfwinreg_registry

from winregrc import catalog
from winregrc import output_writers


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteKeyPath(self, key_path):
    """Writes a key path to the output.

    Args:
      key_path (str): key path.
    """
    self.WriteText(f'{key_path:s}\n')

  def WriteValueDescriptor(self, value_name, value_data_type):
    """Writes a value descriptor to the output.

    Args:
      value_name (str): name of the value.
      value_data_type (str): data type of the value.
    """
    self.WriteText(f'\t{value_name:s}\t{value_data_type:s}\n')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts a catalog of Windows Registry keys and values.'))

  argument_parser.add_argument(
      '--group_keys', '--group-keys', dest='group_keys', action='store_true',
      default=False, help='Group keys with similar values.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help='path of a Windows Registry file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  with open(options.source, 'rb') as file_object:
    try:
      registry_file = dfwinreg_regf.REGFWinRegistryFile()

      registry_file.Open(file_object)
    except IOError:
      registry_file = None

    if not registry_file:
      try:
        registry_file = dfwinreg_creg.CREGWinRegistryFile()

        registry_file.Open(file_object)
      except IOError:
        registry_file = None

    if not registry_file:
      print('Unable to open Windows Registry file.')
      return False

    # Using dfWinReg to determine Windows native key paths if available.
    registry = dfwinreg_registry.WinRegistry()

    key_path_prefix = registry.GetRegistryFileMapping(registry_file)
    registry_file.SetKeyPathPrefix(key_path_prefix)

    root_key = registry_file.GetRootKey()

    output_writer_object = StdoutWriter()

    if not output_writer_object.Open():
      print('Unable to open output writer.')
      print('')
      return False

    collector_object = catalog.CatalogCollector(group_keys=options.group_keys)

    def AlphanumericCompare(key):
      return (int(text) if text.isdigit() else text.lower()
              for text in re.split('([0-9]+)', key[0]))

    try:
      has_results = False
      for key_descriptor in collector_object.Collect(root_key):
        output_writer_object.WriteKeyPath(key_descriptor.key_path)

        for key_path in key_descriptor.grouped_key_paths:
          output_writer_object.WriteKeyPath(key_path)

        for value_name, data_type_string in sorted(
            key_descriptor.value_descriptors, key=AlphanumericCompare):
          output_writer_object.WriteValueDescriptor(
              value_name, data_type_string)

        if options.group_keys:
          output_writer_object.WriteText('\n')

        has_results = True

    finally:
      output_writer_object.Close()

  if not has_results:
    print('No keys and values found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
