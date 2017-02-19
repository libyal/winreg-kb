# -*- coding: utf-8 -*-
"""Windows system information collector."""

from dfwinreg import registry

from winregrc import collector


class WindowsSystemInfoCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows system information collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

  _CURRENT_VERSION_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

  def __init__(self, debug=False, mediator=None):
    """Initializes the collector object.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(WindowsSystemInfoCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  def _GetValueAsStringFromKey(self, key, value_name, default_value=u''):
    """Retrieves a value as a string from the key.

    Args:
      key (dfwinreg.WinRegistryKey): Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not key:
      return default_value

    value = key.GetValueByName(value_name)
    if not value:
      return default_value

    return value.GetDataAsObject()

  def Collect(self, output_writer):
    """Collects the system information.

    Args:
      output_writer (OutputWriter): output writer.
    """
    self.key_found = False

    current_version_key = self._registry.GetKeyByPath(
        self._CURRENT_VERSION_KEY_PATH)
    if not current_version_key:
      return

    self.key_found = True

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

    value = current_version_key.GetValueByName(u'InstallDate')
    if value:
      output_writer.WriteText(
          u'InstallDate: {0:d}'.format(value.GetDataAsObject()))
