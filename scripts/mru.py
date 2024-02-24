#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Most Recently Used (MRU) information."""

import argparse
import logging
import sys

from dfdatetime import fat_date_time as dfdatetime_fat_date_time
from dfdatetime import semantic_time as dfdatetime_semantic_time

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

import pyfwsi

from winregrc import mru
from winregrc import output_writers
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def _WriteShellItemControlPanelCategory(self, shell_item):
    """Writes a control panel category shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    self.WriteValue(
        '\tControl panel category identifier', shell_item.identifier)

  def _WriteShellItemControlPanelItem(self, shell_item):
    """Writes a control panel item shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tControl panel item identifier', shell_item.identifier)

  def _WriteShellItemFileEntry(self, shell_item):
    """Writes a file entry shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tFile size', f'{shell_item.file_size:d}')

    fat_date_time = shell_item.get_modification_time_as_integer()
    if not fat_date_time:
      date_time = dfdatetime_semantic_time.SemanticTime(string='Not set')
    else:
      date_time = dfdatetime_fat_date_time.FATDateTime(
          fat_date_time=fat_date_time)
    self.WriteValue('\tModification time', date_time.CopyToDateTimeString())

    self.WriteValue(
        '\tFile attribute flags',
        f'0x08{shell_item.file_attribute_flags:08x}')

    self.WriteValue('\tName', shell_item.name)

  def _WriteShellItemNetworkLocation(self, shell_item):
    """Writes a network location shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tNetwork location', shell_item.location)

    if shell_item.description:
      self.WriteValue('\tDescription', shell_item.description)

    if shell_item.comments:
      self.WriteValue('\tComments', shell_item.comments)

  def _WriteShellItemVolume(self, shell_item):
    """Writes a volume shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    if shell_item.name:
      self.WriteValue('\tVolume name', shell_item.name)

    if shell_item.identifier:
      self.WriteValue('\tVolume identifier', shell_item.identifier)

    if shell_item.shell_folder_identifier:
      self.WriteValue(
          '\tVolume shell folder identifier',
          shell_item.shell_folder_identifier)

  def WriteShellItem(self, shell_item):
    """Writes a shell item to stdout.

    Args:
      shell_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('Shell item', f'0x{shell_item.class_type:02x}')

    if isinstance(shell_item, pyfwsi.control_panel_category):
      self._WriteShellItemControlPanelCategory(shell_item)

    elif isinstance(shell_item, pyfwsi.control_panel_item):
      self._WriteShellItemControlPanelItem(shell_item)

    elif isinstance(shell_item, pyfwsi.file_entry):
      self._WriteShellItemFileEntry(shell_item)

    elif isinstance(shell_item, pyfwsi.network_location):
      self._WriteShellItemNetworkLocation(shell_item)

    elif isinstance(shell_item, pyfwsi.root_folder):
      self.WriteValue(
          '\tRoot shell folder identifier', shell_item.shell_folder_identifier)

    elif isinstance(shell_item, pyfwsi.volume):
      self._WriteShellItemVolume(shell_item)

    if shell_item.number_of_extension_blocks:
      self.WriteIntegerValueAsDecimal(
          '\tNumber of extension blocks',
          shell_item.number_of_extension_blocks)

      for index, extension_block in enumerate(shell_item.extension_blocks):
        if index > 1:
          self.WriteText('\n')

        self.WriteValue(
            '\tExtension block', f'0x{extension_block.signature:04x}')

        if isinstance(extension_block, pyfwsi.file_entry_extension):
          fat_date_time = extension_block.get_creation_time_as_integer()
          if not fat_date_time:
            date_time = dfdatetime_semantic_time.SemanticTime(string='Not set')
          else:
            date_time = dfdatetime_fat_date_time.FATDateTime(
                fat_date_time=fat_date_time)
          self.WriteValue('\t\tCreation time', date_time.CopyToDateTimeString())

          fat_date_time = extension_block.get_access_time_as_integer()
          if not fat_date_time:
            date_time = dfdatetime_semantic_time.SemanticTime(string='Not set')
          else:
            date_time = dfdatetime_fat_date_time.FATDateTime(
                fat_date_time=fat_date_time)
          self.WriteValue('\t\tAccess time', date_time.CopyToDateTimeString())

          self.WriteValue('\t\tLong name', extension_block.long_name)

          if extension_block.localized_name:
            self.WriteValue(
                '\t\tLocalized name', extension_block.localized_name)

          file_reference = extension_block.file_reference
          if file_reference is not None:
            if file_reference > 0x1000000000000:
              mft_entry = file_reference & 0xffffffffffff
              sequence_number = file_reference >> 48
              file_reference = f'{mft_entry:d}-{sequence_number:d}'
            else:
              file_reference = f'0x{file_reference:04x}'

            self.WriteValue('\t\tFile reference', file_reference)

    self.WriteText('\n')


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
          'a storage media image containing the C:\\Windows directory, '
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

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
    print('')
    return False

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  if not scanner.ScanForWindowsVolume(
      options.source, options=volume_scanner_options):
    print((f'Unable to retrieve the volume with the Windows directory from: '
           f'{options.source:s}.'))
    print('')
    return False

  collector_object = mru.MostRecentlyUsedCollector(
      debug=options.debug, output_writer=output_writer)

  # TODO: change collector to generate MostRecentlyUsedEntry
  result = collector_object.Collect(scanner.registry)
  if not result:
    print('No Most Recently Used key found.')
  else:
    for mru_entry in collector_object.mru_entries:
      output_writer.WriteValue('Key path', mru_entry.key_path)
      output_writer.WriteValue('Value name', mru_entry.value_name)

      if mru_entry.string:
        output_writer.WriteValue('String', mru_entry.string)

      if mru_entry.shell_item_data:
        shell_item = pyfwsi.item()
        shell_item.copy_from_byte_stream(mru_entry.shell_item_data)

        output_writer.WriteShellItem(shell_item)

      elif mru_entry.shell_item_list_data:
        shell_item_list = pyfwsi.item_list()
        shell_item_list.copy_from_byte_stream(mru_entry.shell_item_list_data)

        for shell_item in iter(shell_item_list.items):
          output_writer.WriteShellItem(shell_item)

      output_writer.WriteText('')

  output_writer.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
