#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract shell folder identifiers."""

import argparse
import logging
import sys
import yaml

from winregrc import output_writers
from winregrc import shellfolders
from winregrc import versions
from winregrc import volume_scanner


class StdoutWriter(output_writers.StdoutOutputWriter):
  """Stdout output writer."""

  _WINDOWS_VERSIONS_KEY_FUNCTION = versions.WindowsVersions.KeyFunction

  def WriteHeader(self):
    """Writes the header to stdout."""
    print('# winreg-kb shellfolder definitions')

  def WriteShellFolder(self, shell_folder, windows_versions):
    """Writes the shell folder to stdout.

    Args:
      shell_folder (WindowsShellFolder): the shell folder.
      windows_versions (list[str]): the Windows versions.
    """
    print('---')
    print(f'identifier: "{shell_folder.identifier:s}"')

    if shell_folder.class_name:
      print(f'class_name: {shell_folder.class_name:s}')

    name = shell_folder.name
    if '\\' in name:
      name = name.replace('\\', '\\\\')

    if shell_folder.name:
      print(f'name: "{name:s}"')

    if shell_folder.alternate_names:
      alternate_names = ', '.join([
          f'"{name:s}"' for name in shell_folder.alternate_names])
      print(f'alternate_names: [{alternate_names:s}]')

    windows_versions = ', '.join([f'"{version:s}"' for version in sorted(
        windows_versions, key=self._WINDOWS_VERSIONS_KEY_FUNCTION)])
    print(f'windows_versions: [{windows_versions:s}]')


def Main():
  """Entry point of console script to extract shell folder identifiers.

  Returns:
    int: exit code that is provided to sys.exit().
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts the shell folder identifiers from the Windows Registry.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      '-w', '--windows_version', '--windows-version', dest='windows_version',
      action='store', metavar='VERSION', default=None,
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
      # TODO: compare attributes with existing with shell folder.
      existing_shell_folder = shell_folder_per_identifier.get(
          shell_folder.identifier, None)

      if not existing_shell_folder:
        shell_folder_per_identifier[shell_folder.identifier] = shell_folder
      elif not existing_shell_folder.name:
        existing_shell_folder.name = shell_folder.name
      elif (shell_folder.name and
            shell_folder.name != existing_shell_folder.name and
            shell_folder.name not in existing_shell_folder.alternate_names):
        existing_shell_folder.alternate_names.append(shell_folder.name)

      if windows_version:
        if shell_folder.identifier not in windows_versions_per_shell_folder:
          windows_versions_per_shell_folder[shell_folder.identifier] = []

        windows_versions_per_shell_folder[shell_folder.identifier].append(
            windows_version)

  if not shell_folder_per_identifier:
    print('No shell folder identifiers found.')
    return 0

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return 1

  try:
    output_writer_object.WriteHeader()
    for identifier, windows_versions in sorted(
        windows_versions_per_shell_folder.items()):
      shell_folder = shell_folder_per_identifier[identifier]
      output_writer_object.WriteShellFolder(shell_folder, windows_versions)

  finally:
    output_writer_object.Close()

  return 0


if __name__ == '__main__':
  sys.exit(Main())
