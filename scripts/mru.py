#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Most Recently Used (MRU) information."""

import argparse
import logging
import sys

from dfvfs.lib import errors as dfvfs_errors

import pyfwps
import pyfwsi

from winregrc import mru
from winregrc import output_writers
from winregrc import shell_property_keys
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def _WritePropertyStore(self, fwps_store):
    """Writes a property store to stdout.

    Args:
      fwps_store (pyfwps.store): property store.

    Raises:
      RuntimeError: if a property value type is not supported.
    """
    for fwps_set in iter(fwps_store.sets):
      for fwps_record in iter(fwps_set.records):
        if fwps_record.value_type == 0x0001:
          value_string = '<VT_NULL>'
        elif fwps_record.value_type in (0x0003, 0x0013, 0x0014, 0x0015):
          value_string = str(fwps_record.get_data_as_integer())
        elif fwps_record.value_type in (0x0008, 0x001e, 0x001f):
          value_string = fwps_record.get_data_as_string()
        elif fwps_record.value_type == 0x000b:
          value_string = str(fwps_record.get_data_as_boolean())
        elif fwps_record.value_type == 0x0040:
          filetime = fwps_record.get_data_as_integer()
          value_string = self._FormatFiletimeValue(filetime)
        elif fwps_record.value_type == 0x0042:
          # TODO: add support
          value_string = '<VT_STREAM>'
        elif fwps_record.value_type == 0x0048:
          value_string = fwps_record.get_data_as_guid()
        elif fwps_record.value_type & 0xf000 == 0x1000:
          # TODO: add support
          value_string = '<VT_VECTOR>'
        else:
          raise RuntimeError(
              f'Unsupported value type: 0x{fwps_record.value_type:04x}')

        if fwps_record.entry_name:
          entry_string = fwps_record.entry_name
        else:
          entry_string = f'{fwps_record.entry_type:d}'

        property_key = f'{{{fwps_set.identifier:s}}}/{entry_string:s}'
        shell_property_key = shell_property_keys.SHELL_PROPERTY_KEYS.get(
            property_key, 'Unknown')
        self.WriteText(
            f'\tProperty: {property_key:s} ({shell_property_key:s})\n')

        self.WriteValue(
            f'\t\tValue (0x{fwps_record.value_type:04x})', value_string)

  def _WriteShellItem(self, fwsi_item):
    """Writes a shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if isinstance(fwsi_item, pyfwsi.control_panel_category):
      shell_item_type = 'Control Panel Category'
    elif isinstance(fwsi_item, pyfwsi.control_panel_item):
      shell_item_type = 'Control Panel Item'
    elif isinstance(fwsi_item, pyfwsi.file_entry):
      shell_item_type = 'File Entry'
    elif isinstance(fwsi_item, pyfwsi.network_location):
      shell_item_type = 'Network Location'
    elif isinstance(fwsi_item, pyfwsi.root_folder):
      shell_item_type = 'Root Folder'
    elif isinstance(fwsi_item, pyfwsi.users_property_view):
      shell_item_type = 'Users Property View'
    elif isinstance(fwsi_item, pyfwsi.volume):
      shell_item_type = 'Volume'
    else:
      shell_item_type = f'Unknown (0x{fwsi_item.class_type:02x})'

    self.WriteValue('\tItem type', shell_item_type)

    if fwsi_item.delegate_folder_identifier:
      self.WriteValue(
          '\tDelegate folder', fwsi_item.delegate_folder_identifier)

    if isinstance(fwsi_item, pyfwsi.control_panel_category):
      self._WriteShellItemControlPanelCategory(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.control_panel_item):
      self._WriteShellItemControlPanelItem(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.file_entry):
      self._WriteShellItemFileEntry(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.network_location):
      self._WriteShellItemNetworkLocation(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.root_folder):
      self.WriteValue(
          '\tRoot shell folder identifier', fwsi_item.shell_folder_identifier)

    elif isinstance(fwsi_item, pyfwsi.users_property_view):
      self._WriteShellItemUsersPropertyView(fwsi_item)

    elif isinstance(fwsi_item, pyfwsi.volume):
      self._WriteShellItemVolume(fwsi_item)

    if fwsi_item.number_of_extension_blocks:
      self.WriteValue(
          '\tNumber of extension blocks',
          f'{fwsi_item.number_of_extension_blocks:d}')

      for index, extension_block in enumerate(fwsi_item.extension_blocks):
        display_index = index + 1
        self.WriteText(f'Extension block: {display_index:d}\n')

        # TODO: print human readable description of signature
        self.WriteValue('\tSignature', f'0x{extension_block.signature:04x}')

        if isinstance(extension_block, pyfwsi.file_entry_extension):
          fat_date_time = extension_block.get_creation_time_as_integer()
          date_time_string = self._FormatFATDateTimeValue(fat_date_time)
          self.WriteValue('\tCreation time', date_time_string)

          fat_date_time = extension_block.get_access_time_as_integer()
          date_time_string = self._FormatFATDateTimeValue(fat_date_time)
          self.WriteValue('\tAccess time', date_time_string)

          self.WriteValue('\tLong name', extension_block.long_name)

          if extension_block.localized_name:
            self.WriteValue(
                '\tLocalized name', extension_block.localized_name)

          file_reference = extension_block.file_reference
          if file_reference is not None:
            if file_reference > 0x1000000000000:
              mft_entry = file_reference & 0xffffffffffff
              sequence_number = file_reference >> 48
              file_reference = f'{mft_entry:d}-{sequence_number:d}'
            else:
              file_reference = f'0x{file_reference:04x}'

            self.WriteValue('\tFile reference', file_reference)

        # TODO: add support for other extension blocks

    self.WriteText('\n')
  def _WriteShellItemControlPanelCategory(self, fwsi_item):
    """Writes a control panel category shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue(
        '\tControl panel category identifier', f'{fwsi_item.identifier:d}')

  def _WriteShellItemControlPanelItem(self, fwsi_item):
    """Writes a control panel item shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tControl panel item identifier', fwsi_item.identifier)

  def _WriteShellItemFileEntry(self, fwsi_item):
    """Writes a file entry shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tFile size', f'{fwsi_item.file_size:d}')

    fat_date_time = fwsi_item.get_modification_time_as_integer()
    date_time_string = self._FormatFATDateTimeValue(fat_date_time)
    self.WriteValue('\tModification time', date_time_string)

    self.WriteValue(
        '\tFile attribute flags',
        f'0x08{fwsi_item.file_attribute_flags:08x}')

    self.WriteValue('\tName', fwsi_item.name)

  def _WriteShellItemNetworkLocation(self, fwsi_item):
    """Writes a network location shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteValue('\tNetwork location', fwsi_item.location)

    if fwsi_item.description:
      self.WriteValue('\tDescription', fwsi_item.description)

    if fwsi_item.comments:
      self.WriteValue('\tComments', fwsi_item.comments)

  def _WriteShellItemUsersPropertyView(self, fwsi_item):
    """Writes an users property view item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if fwsi_item.property_store_data:
      fwps_store = pyfwps.store()
      fwps_store.copy_from_byte_stream(fwsi_item.property_store_data)

      self._WritePropertyStore(fwps_store)

  def _WriteShellItemVolume(self, fwsi_item):
    """Writes a volume shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    if fwsi_item.name:
      self.WriteValue('\tVolume name', fwsi_item.name)

    if fwsi_item.identifier:
      self.WriteValue('\tVolume identifier', fwsi_item.identifier)

    if fwsi_item.shell_folder_identifier:
      self.WriteValue(
          '\tVolume shell folder identifier',
          fwsi_item.shell_folder_identifier)

  def WriteShellItem(self, fwsi_item):
    """Writes a shell item to stdout.

    Args:
      fwsi_item (pyfwsi.item): Shell item.
    """
    self.WriteText('Shell item:\n')
    self._WriteShellItem(fwsi_item)

  def WriteShellItemList(self, fwsi_item_list):
    """Writes a shell item list to stdout.

    Args:
      fwsi_item_list (pyfwsi.item_list): Shell item list.
    """
    self.WriteText('Shell item list:\n')
    self.WriteValue('\tNumber of items', fwsi_item_list.number_of_items)
    self.WriteText('\n')

    for item_index, fwsi_item in enumerate(fwsi_item_list.items):
      display_item_index = item_index + 1
      self.WriteText(f'Shell item: {display_item_index:d}\n')

      self._WriteShellItem(fwsi_item)


def Main():
  """Entry point of console script to extract Most Recently Used information.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Most Recently Used information from a NTUSER.DAT Registry '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-u', '--username', dest='username', action='store', metavar='USERNAME',
      default=None, help='username within a storage media image.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a NTUSER.DAT or UsrClass.dat Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return 1

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
    print('')
    return 1

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.username = options.username
  volume_scanner_options.volumes = ['none']

  try:
    result = scanner.ScanForWindowsVolume(
        options.source, options=volume_scanner_options)

  except dfvfs_errors.ScannerError as exception:
    print(f'[ERROR] {exception!s}', file=sys.stderr)
    print('')
    return 1

  except KeyboardInterrupt:
    print('Aborted by user.', file=sys.stderr)
    print('')
    return 1

  if not result:
    print((f'Unable to retrieve the volume with the Windows directory from: '
           f'{options.source:s}.'))
    print('')
    return 1

  collector_object = mru.MostRecentlyUsedCollector(
      debug=options.debug, output_writer=output_writer)

  # TODO: change collector to generate MostRecentlyUsedEntry
  result = collector_object.Collect(scanner.registry)
  if not result:
    print('No Most Recently Used key found.')
    return 0

  for mru_entry in collector_object.mru_entries:
    output_writer.WriteValue('Key path', mru_entry.key_path)
    output_writer.WriteValue('Value name', mru_entry.value_name)

    if mru_entry.string:
      output_writer.WriteValue('String', mru_entry.string)
      output_writer.WriteText('\n')

    if mru_entry.shell_item_data:
      fwsi_item = pyfwsi.item()
      fwsi_item.copy_from_byte_stream(mru_entry.shell_item_data)

      output_writer.WriteShellItem(fwsi_item)

    elif mru_entry.shell_item_list_data:
      shell_item_list = pyfwsi.item_list()
      shell_item_list.copy_from_byte_stream(mru_entry.shell_item_list_data)

      output_writer.WriteShellItemList(shell_item_list)

  output_writer.Close()

  return 0


if __name__ == '__main__':
  sys.exit(Main())
