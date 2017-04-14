# -*- coding: utf-8 -*-
"""Shell Folder collector."""

from __future__ import print_function

from winregrc import interface


class ShellFolder(object):
  """Shell folder."""

  def __init__(self, guid, name, localized_string):
    """Initializes a shell folder.

    Args:
      guid (str): GUID.
      name (str): name.
      localized_string (str): localized string of the name.
    """
    super(ShellFolder, self).__init__()
    self.guid = guid
    self.name = name
    self.localized_string = localized_string


class ShellFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Shell folder collector."""

  _CLASS_IDENTIFIERS_KEY_PATH = u'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def Collect(self, registry, output_writer):
    """Collects the shell folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the shell folders key was found, False if not.
    """
    result = False
    class_identifiers_key = registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if not class_identifiers_key:
      return

    for class_identifier_key in class_identifiers_key.GetSubkeys():
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.GetSubkeyByName(u'ShellFolder')
      if shell_folder_key:
        result = True

        value = class_identifier_key.GetValueByName(u'')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode(u'utf-16-le').lstrip(u'\x00')
        else:
          name = u''

        value = class_identifier_key.GetValueByName(u'LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode(u'utf-16-le').lstrip(u'\x00')
        else:
          localized_string = u''

        shell_folder = ShellFolder(guid, name, localized_string)
        output_writer.WriteShellFolder(shell_folder)

    return result
