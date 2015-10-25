# -*- coding: utf-8 -*-

from __future__ import print_function
import logging
import os

import sqlite3

from winreg_kb import collector
from winreg_kb import registry


# pylint: disable=logging-format-interpolation

class ShellFolder(object):
  """Class that defines a shell folder."""

  def __init__(self, guid, name, localized_string):
    """Initializes the shell folder object.

    Args:
      guid: the GUID.
      name: the name.
      localized_string: localized string of the name.
    """
    super(ShellFolder, self).__init__()
    self.guid = guid
    self.name = name
    self.localized_string = localized_string


class ShellFolderIdentifierCollector(collector.WindowsVolumeCollector):
  """Class that defines a Shell Folder identifier collector."""

  _CLASS_IDENTIFIERS_KEY_PATH = u'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def __init__(self):
    """Initializes the Shell Folder identifier collector object."""
    super(ShellFolderIdentifierCollector, self).__init__()
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(registry_file_reader)

    self.found_class_identifiers_key = False
    self.found_shell_folder_identifier_key = False

  def Collect(self, output_writer):
    """Collects the Shell Folder identifiers.

    Args:
      output_writer: the output writer object.
    """
    self.found_class_identifiers_key = False
    class_identifiers_key = self._registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if not class_identifiers_key:
      return

    self.found_class_identifiers_key = True
    for class_identifier_key in class_identifiers_key.sub_keys:
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.get_sub_key_by_name(
          u'ShellFolder')
      if shell_folder_key:
        self.found_shell_folder_identifier_key = True

        value = class_identifier_key.get_value_by_name(u'')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode(u'utf-16-le')[:-1]
        else:
          name = u''

        value = class_identifier_key.get_value_by_name(u'LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode(u'utf-16-le')[:-1]
        else:
          localized_string = u''

        shell_folder = ShellFolder(guid, name, localized_string)
        output_writer.WriteShellFolder(shell_folder)
