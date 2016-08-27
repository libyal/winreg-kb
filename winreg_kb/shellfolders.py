# -*- coding: utf-8 -*-
"""Shell Folder identifier collector."""

from __future__ import print_function

from dfwinreg import registry

from winreg_kb import collector


class ShellFolder(object):
  """Class that defines a shell folder."""

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


class ShellFolderIdentifierCollector(collector.WindowsVolumeCollector):
  """Class that defines a Shell Folder identifier collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

  _CLASS_IDENTIFIERS_KEY_PATH = u'HKEY_LOCAL_MACHINE\\Software\\Classes\\CLSID'

  def __init__(self, debug=False, mediator=None):
    """Initializes the collector object.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(ShellFolderIdentifierCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  def Collect(self, output_writer):
    """Collects the Shell Folder identifiers.

    Args:
      output_writer (OutputWriter): output writer.
    """
    self.key_found = False
    class_identifiers_key = self._registry.GetKeyByPath(
        self._CLASS_IDENTIFIERS_KEY_PATH)
    if not class_identifiers_key:
      return

    for class_identifier_key in class_identifiers_key.GetSubkeys():
      guid = class_identifier_key.name.lower()

      shell_folder_key = class_identifier_key.GetSubkeyByName(u'ShellFolder')
      if shell_folder_key:
        self.key_found = True

        value = class_identifier_key.GetValueByName(u'')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          name = value.data.decode(u'utf-16-le')[:-1]
        else:
          name = u''

        value = class_identifier_key.GetValueByName(u'LocalizedString')
        if value:
          # The value data type does not have to be a string therefore try to
          # decode the data as an UTF-16 little-endian string and strip
          # the trailing end-of-string character
          localized_string = value.data.decode(u'utf-16-le')[:-1]
        else:
          localized_string = u''

        shell_folder = ShellFolder(guid, name, localized_string)
        output_writer.WriteShellFolder(shell_folder)
