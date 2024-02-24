# -*- coding: utf-8 -*-
"""Windows Shell folder collector."""

from acstore.containers import interface as containers_interface
from acstore.containers import manager as containers_manager

from winregrc import interface


class WindowsShellFolder(containers_interface.AttributeContainer):
  """Windows Shell folder.

  Attributes:
    class_name (str): class name (CLSID).
    identifier (str): identifier (GUID).
    name (str): name.
    localized_string (str): localized string of the name.
  """

  CONTAINER_TYPE = 'windows_shell_folder'

  SCHEMA = {
      'class_name': 'str',
      'identifier': 'str',
      'localized_string': 'str',
      'name': 'str'}

  def __init__(self, identifier=None, localized_string=None):
    """Initializes a Windows Shell folder.

    Args:
      identifier (Optional[str]): identifier (GUID).
      localized_string (Optional[str]): localized string of the name.
    """
    super(WindowsShellFolder, self).__init__()
    self.class_name = None
    self.identifier = identifier
    self.localized_string = localized_string
    self.name = None


class ShellFoldersCollector(interface.WindowsRegistryKeyCollector):
  """Windows Shell folder collector."""

  _CLASS_IDENTIFIERS_KEY_PATH = 'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def _CollectShellFolders(self, class_identifiers_key):
    """Collects Windows Shell folders.

    Args:
      class_identifiers_key (dfwinreg.WinRegistry): CLSID Windows Registry.

    Yields:
      ShellFolder: a Windows Shell folder.
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
          name = value.data.decode('utf-16-le').rstrip('\x00')
        else:
          name = None

        # TODO: resolve name MUI paths.

        value = class_identifier_key.GetValueByName('LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode('utf-16-le').rstrip('\x00')
        else:
          localized_string = None

        shell_folder = WindowsShellFolder(
            identifier=guid, localized_string=localized_string)
        if name and name.startswith('CLSID_'):
          shell_folder.class_name = name
        else:
          shell_folder.name = name

        yield shell_folder

  def Collect(self, registry):
    """Collects Windows Shell folders.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      WindowsShellFolder: a Windows Shell folder.
    """
    class_identifiers_key = registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if class_identifiers_key:
      yield from self._CollectShellFolders(class_identifiers_key)


containers_manager.AttributeContainersManager.RegisterAttributeContainer(
    WindowsShellFolder)
