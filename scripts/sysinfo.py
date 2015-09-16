#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import sys

import collector
import registry


class WindowsSystemInfoCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows system information collector."""

  DEFAULT_VALUE_NAME = u''

  _CURRENT_VERSION_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

  def __init__(self):
    """Initializes the Windows system information collector object."""
    super(WindowsSystemInfoCollector, self).__init__()
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(registry_file_reader)

    self.found_current_version_key = False

  def _GetValueAsStringFromKey(self, key, value_name, default_value=u''):
    """Retrieves a value as a string from the key.

    Args:
      key: the key object (instance of pyregf.key).
      value_name: string containing the name of the value.
      default_value: optional default value. The default is an empty string.

    Returns:
      The value as a string or the default value if not available.
    """
    if not key:
      return default_value

    value = key.get_value_by_name(value_name)
    if not value:
      return default_value

    return value.get_data_as_string()

  def Collect(self, output_writer):
    """Collects the system information.

    Args:
      output_writer: the output writer object.
    """
    self.found_current_version_key = False

    current_version_key = self._registry.GetKeyByPath(
        self._CURRENT_VERSION_KEY_PATH)
    if not current_version_key:
      return

    self.found_current_version_key = True

    value_names = [
        u'ProductName',
        u'CSDVersion',
        u'CurrentVersion',
        u'CurrentBuildNumber',
        u'CurrentType',
        u'ProductId',
        u'RegisteredOwner',
        u'RegisteredOrganization',
        u'PathName',
        u'SystemRoot',
    ]

    for value_name in value_names:
      value_string = self._GetValueAsStringFromKey(
          current_version_key, value_name)
      output_writer.WriteText(u'{0:s}: {1:s}'.format(value_name, value_string))

    value = current_version_key.get_value_by_name(u'InstallDate')
    if value:
      output_writer.WriteText(u'InstallDate: {0:d}'.format(
          value.get_data_as_integer()))


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Close(self):
    """Closes the output writer object."""
    return

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text: the text to write.
    """
    print(text)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extract the system information from a SOFTWARE Registry File (REGF).'))

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SOFTWARE Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = WindowsSystemInfoCollector()

  if not collector_object.GetWindowsVolumePathSpec(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.Collect(output_writer)
  output_writer.Close()

  if not collector_object.found_current_version_key:
    print(u'No current version key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
