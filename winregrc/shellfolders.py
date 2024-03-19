# -*- coding: utf-8 -*-
"""Windows Shell folder collector."""

from winregrc import interface


class WindowsShellFolder(object):
  """Windows Shell folder.

  Attributes:
    alternate_names (list[str]): alternate names.
    class_name (str): class name (CLSID).
    identifier (str): identifier (GUID).
    name (str): name.
    localized_string (str): localized string of the name.
  """

  def __init__(self, identifier=None, localized_string=None):
    """Initializes a Windows Shell folder.

    Args:
      identifier (Optional[str]): identifier (GUID).
      localized_string (Optional[str]): localized string of the name.
    """
    super(WindowsShellFolder, self).__init__()
    self.alternate_names = []
    self.class_name = None
    self.identifier = identifier
    self.localized_string = localized_string
    self.name = None


class ShellFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Windows Shell folder collector."""

  _CLASS_IDENTIFIERS_KEY_PATH = 'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def __init__(self, debug=False):
    """Initializes a Windows Registry key and value collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
    """
    super(ShellFoldersCollector, self).__init__(debug=debug)
    self._ascii_codepage = 'cp1252'

  def _CollectShellFolders(self, class_identifiers_key):
    """Collects Windows Shell folders.

    Args:
      class_identifiers_key (dfwinreg.WinRegistry): CLSID Windows Registry.

    Yields:
      ShellFolder: a Windows Shell folder.
    """
    for class_identifier_key in class_identifiers_key.GetSubkeys():
      shell_folder_identifier = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.GetSubkeyByName('ShellFolder')
      if shell_folder_key:
        name = self._GetShellFolderName(class_identifier_key)

        value = class_identifier_key.GetValueByName('LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode('utf-16-le').rstrip('\x00')
        else:
          localized_string = None

        shell_folder = WindowsShellFolder(
            identifier=shell_folder_identifier,
            localized_string=localized_string)
        if name and name.startswith('CLSID_'):
          shell_folder.class_name = name
        else:
          shell_folder.name = name

        yield shell_folder

  def _GetShellFolderName(self, class_identifier_key):
    """Retrieves the shell folder name.

    Args:
      class_identifier_key (dfwinreg.RegistryKey): class identifier Windows
          Registry key.

    Returns:
      str: shell folder name or None if not available.
    """
    value = class_identifier_key.GetValueByName('')
    if not value or not value.data:
      return None

    # First try to decode the value data as an UTF-16 little-endian string with
    # end-of-string character
    try:
      return value.data.decode('utf-16-le').rstrip('\x00')
    except UnicodeDecodeError:
      pass

    # Next try to decode the value data as an ASCII string with a specific
    # codepage and end-of-string character.
    try:
      return value.data.decode(self._ascii_codepage).rstrip('\x00')
    except UnicodeDecodeError:
      pass

    return None

  def Collect(self, registry):
    """Collects Windows Shell folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      WindowsShellFolder: a Windows Shell folder.
    """
    # TODO: Add support for per-user shell folders

    class_identifiers_key = registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if class_identifiers_key:
      yield from self._CollectShellFolders(class_identifiers_key)
