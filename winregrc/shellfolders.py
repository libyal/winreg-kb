# -*- coding: utf-8 -*-
"""Shell Folder collector."""

from winregrc import interface


class ShellFolder(object):
  """Shell folder.

  Attributes:
    guid (str): GUID.
    name (str): name.
    localized_string (str): localized string of the name.
  """

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

  _CLASS_IDENTIFIERS_KEY_PATH = 'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def _CollectShellFolders(self, class_identifiers_key):
    """Collects the shell folders.

    Args:
      class_identifiers_key (dfwinreg.WinRegistry): CLSID Windows Registry.

    Yields:
      ShellFolder: a shell folder.
    """
    for class_identifier_key in class_identifiers_key.GetSubkeys():
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.GetSubkeyByName('ShellFolder')
      if shell_folder_key:
        value = class_identifier_key.GetValueByName('')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode('utf-16-le').lstrip('\x00')
        else:
          name = ''

        value = class_identifier_key.GetValueByName('LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode('utf-16-le').lstrip('\x00')
        else:
          localized_string = ''

        yield ShellFolder(guid, name, localized_string)

  def Collect(self, registry):
    """Collects the shell folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      ShellFolder: a shell folder.
    """
    class_identifiers_key = registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if class_identifiers_key:
      yield from self._CollectShellFolders(class_identifiers_key)
