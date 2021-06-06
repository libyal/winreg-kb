#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract a catalog of Windows Registry keys and values."""

import argparse
import logging
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
    text = '{0:s}\n'.format(key_path)
    self.WriteText(text)

  def WriteValueDescriptor(self, value_name, value_data_type):
    """Writes a value descriptor to the output.

    Args:
      value_name (str): name of the value.
      value_data_type (str): data type of the value.
    """
    text = '\t{0:s}\t{1:s}\n'.format(value_name, value_data_type)
    self.WriteText(text)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts a catalog of Windows Registry keys and values.'))

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

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  file_object = open(options.source, 'rb')

  try:
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

    result = False
    if root_key:
      collector_object = catalog.CatalogCollector()
      result = collector_object.Collect(root_key, output_writer_object)

    if not result:
      print('No catalog keys and values found.')

  finally:
    file_object.close()

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
