#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Windows control panel items from the Windows Registry."""

import argparse
import logging
import sys
import yaml

from winregrc import controlpanel_items
from winregrc import output_writers
from winregrc import versions
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  _WINDOWS_VERSIONS_KEY_FUNCTION = versions.WindowsVersions.KeyFunction

  def WriteHeader(self):
    """Writes the header to stdout."""
    print('# winreg-kb controlpanel items definitions')

  def WriteKnownFolder(self, control_panel_item, windows_versions):
    """Writes the control panel item to stdout.

    Args:
      control_panel_item (KnownFolder): the control panel item.
      windows_versions (list[str]): the Windows versions.
    """
    print('---')
    print(f'identifier: "{control_panel_item.identifier:s}"')
    if control_panel_item.module_name:
      print(f'module_name: "{control_panel_item.module_name:s}"')

    if control_panel_item.alternate_module_names:
      alternate_module_names = ', '.join([
          f'"{name:s}"' for name in control_panel_item.alternate_module_names])
      print(f'alternate_module_names: [{alternate_module_names:s}]')

    windows_versions = ', '.join([f'"{version:s}"' for version in sorted(
        windows_versions, key=self._WINDOWS_VERSIONS_KEY_FUNCTION)])
    print(f'windows_versions: [{windows_versions:s}]')


def Main():
  """Entry point of console script to extract control panel items.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Windows control panel items from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-w', '--windows_version', '--windows-version', dest='windows_version',
      action='store', metavar='VERSION', default=None,
      help='string that identifies the Windows version.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory, '
          'or the path of a SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return 1

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  try:
    with open(options.source, 'r', encoding='utf-8') as file_object:
      source_definitions = list(yaml.safe_load_all(file_object))

  except (SyntaxError, UnicodeDecodeError, yaml.parser.ParserError):
    source_definitions = [{
        'source': options.source, 'windows_version': options.windows_version}]

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.username = ['none']
  volume_scanner_options.volumes = ['none']

  control_panel_item_per_identifier = {}
  windows_versions_per_control_panel_item = {}

  for source_definition in source_definitions:
    source_path = source_definition['source']
    logging.info(f'Processing: {source_path:s}')

    if not scanner.ScanForWindowsVolume(
        source_path, options=volume_scanner_options):
      logging.error((
          f'Unable to retrieve the volume with the Windows directory from: '
          f'{source_path:s}.'))
      continue

    collector_object = controlpanel_items.ControlPanelItemsCollector(
        debug=options.debug)

    # TODO: determine Windows version from source.
    windows_version = source_definition['windows_version']

    for item in collector_object.Collect(scanner.registry):
      # TODO: compare attributes with existing item.
      existing_item = control_panel_item_per_identifier.get(
          item.identifier, None)

      # Ignore a module name that is the same as the identifier.
      if (item.module_name and
          item.module_name.lower() == item.identifier):
        item.module_name = None

      if not existing_item:
        control_panel_item_per_identifier[item.identifier] = item
      elif not existing_item.module_name:
        existing_item.module_name = item.module_name
      elif (item.module_name and
            item.module_name != existing_item.module_name and
            item.module_name not in existing_item.alternate_module_names):
        existing_item.alternate_module_names.append(item.module_name)

      if item.identifier not in (
          windows_versions_per_control_panel_item):
        windows_versions_per_control_panel_item[item.identifier] = []

      if windows_version:
        windows_versions_per_control_panel_item[item.identifier].append(
            windows_version)

  if not control_panel_item_per_identifier:
    print('No control panel items found.')
    return 0

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return 1

  try:
    output_writer_object.WriteHeader()
    for identifier, windows_versions in sorted(
        windows_versions_per_control_panel_item.items()):
      control_panel_item = control_panel_item_per_identifier[identifier]
      output_writer_object.WriteKnownFolder(
          control_panel_item, windows_versions)

  finally:
    output_writer_object.Close()

  return 0


if __name__ == '__main__':
  sys.exit(Main())
