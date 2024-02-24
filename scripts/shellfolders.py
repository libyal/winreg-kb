#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract shell folder class identifiers."""

import argparse
import logging
import sys
import yaml

from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner

from winregrc import output_writers
from winregrc import shellfolders
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  def WriteHeader(self):
    """Writes the header to stdout."""
    print('# winreg-kb shellfolder definitions')
    print('---')

  def WriteShellFolder(self, shell_folder, windows_versions):
    """Writes the shell folder to stdout.

    Args:
      shell_folder (WindowsShellFolder): the shell folder.
      windows_versions (list[str]): the Windows versions.
    """
    print(f'identifier: "{shell_folder.identifier:s}"')

    if shell_folder.class_name:
      print(f'class_name: {shell_folder.class_name:s}')

    if shell_folder.name:
      print(f'name: "{shell_folder.name:s}"')

    windows_versions = ', '.join([
      f'"{version:s}"' for version in sorted(windows_versions)])
    print(f'windows_versions: [{windows_versions:s}]')
    print('---')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the shell folder class identifiers from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-w', '--windows_version', '--windows-version', dest='windows_version',
      action='store', metavar='Windows XP', default=None,
      help='string that identifies the Windows version.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None, help=(
          'path of the volume containing C:\\Windows, the filename of a '
          'storage media image containing the C:\\Windows directory, or the '
          'path of a SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  try:
    with open(options.source, 'r', encoding='utf-8') as file_object:
      source_definitions = list(yaml.safe_load_all(file_object))

  except (SyntaxError, UnicodeDecodeError):
    source_definitions = [{
        'source': options.source, 'windows_version': options.windows_version}]

  mediator = volume_scanner.WindowsRegistryVolumeScannerMediator()
  scanner = volume_scanner.WindowsRegistryVolumeScanner(mediator=mediator)

  volume_scanner_options = dfvfs_volume_scanner.VolumeScannerOptions()
  volume_scanner_options.partitions = ['all']
  volume_scanner_options.snapshots = ['none']
  volume_scanner_options.volumes = ['none']

  shell_folder_per_identifier = {}
  windows_versions_per_shell_folder = {}

  for source_definition in source_definitions:
    source_path = source_definition['source']
    logging.info(f'Processing: {source_path:s}')

    if not scanner.ScanForWindowsVolume(
        source_path, options=volume_scanner_options):
      logging.error((
          f'Unable to retrieve the volume with the Windows directory from: '
          f'{source_path:s}.'))
      continue

    # TODO: map collector to available Registry keys.
    collector_object = shellfolders.ShellFoldersCollector(
        debug=options.debug)

    # TODO: determine Windows version from source.
    windows_version = source_definition['windows_version']

    for shell_folder in collector_object.Collect(scanner.registry):
      # TODO: compare existing shell folder
      shell_folder_per_identifier[shell_folder.identifier] = shell_folder

      if shell_folder.identifier not in windows_versions_per_shell_folder:
        windows_versions_per_shell_folder[shell_folder.identifier] = []

      windows_versions_per_shell_folder[shell_folder.identifier].append(
          windows_version)

  if not shell_folder_per_identifier:
    print('No shell folder identifiers found.')
    return True

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  try:
    output_writer_object.WriteHeader()
    for identifier, windows_versions in sorted(
        windows_versions_per_shell_folder.items()):
      shell_folder = shell_folder_per_identifier[identifier]
      output_writer_object.WriteShellFolder(shell_folder, windows_versions)

  finally:
    output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
