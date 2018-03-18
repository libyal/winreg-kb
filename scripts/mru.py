#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Most Recently Used (MRU) information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

import pyfwsi

from winregrc import collector
from winregrc import output_writer
from winregrc import mru


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text (bytes): text to write.
    """
    print(text)

  def _WriteShellItem(self, shell_item):
    """Writes a shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell Item to write.
    """
    value_string = '0x{0:02x}'.format(shell_item.class_type)
    self.WriteValue('Shell item', value_string)

    self.WriteIntegerValueAsDecimal(
        '\tNumber of extension blocks', shell_item.number_of_extension_blocks)

    for extension_block in shell_item.extension_blocks:
      self._WriteShellItemExtensionBlock(extension_block)

  def _WriteShellItemExtensionBlock(self, extension_block):
    """Writes a shell item extension block to stdout.

    Args:
      extension_block (pyfwsi.extension_block): Shell Item extension block to
          write.
    """
    value_string = '0x{0:04x}'.format(extension_block.signature)
    self.WriteValue('\tExtension block', value_string)

  def WriteMostRecentlyUsedEntry(self, mru_entry):
    """Writes a Most Recently Used (MRU) entry to stdout.

    Args:
      mru_entry (MostRecentlyUsedEntry): MRU entry to write.
    """
    if mru_entry.string:
      self.WriteValue('String', mru_entry.string)

    if mru_entry.shell_item_data:
      shell_item = pyfwsi.item()
      shell_item.copy_from_byte_stream(mru_entry.shell_item_data)

      self._WriteShellItem(shell_item)

    elif mru_entry.shell_item_list_data:
      shell_item_list = pyfwsi.item_list()
      shell_item_list.copy_from_byte_stream(mru_entry.shell_item_list_data)

      for shell_item in iter(shell_item_list.items):
        self._WriteShellItem(shell_item)

    self.WriteText('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Most Recently Used information from a NTUSER.DAT Registry '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory,'
          'or the path of a NTUSER.DAT Registry file.'))

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

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = mru.MostRecentlyUsedCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No Most Recently Used key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
