# -*- coding: utf-8 -*-
"""System information collector."""

from dfdatetime import posix_time as dfdatetime_posix_time
from dfdatetime import semantic_time as dfdatetime_semantic_time

from winregrc import interface


class SystemInformation(object):
  """System information.

  Attributes:
    csd_version (str): CSD version.
    current_build_number (str): current build number.
    current_type (str): current type.
    current_version (str): current version.
    installation_date (dfdatetime.DateTimeValues): installation date and time.
    path_name (str): path name.
    product_identifier (str): product identifier.
    product_name (str): product name.
    registered_organization (str): registered organization.
    registered_owner (str): registered owner.
    system_root (str): system root path.
  """

  def __init__(self):
    """Initializes system information."""
    super(SystemInformation, self).__init__()
    self.csd_version = None
    self.current_build_number = None
    self.current_type = None
    self.current_version = None
    self.installation_date = None
    self.path_name = None
    self.product_identifier = None
    self.product_name = None
    self.registered_organization = None
    self.registered_owner = None
    self.system_root = None


class SystemInfoCollector(interface.WindowsRegistryKeyCollector):
  """System information collector."""

  _CURRENT_VERSION_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

  _STRING_VALUES = {
      u'CSDVersion': u'csd_version',
      u'CurrentBuildNumber': u'current_build_number',
      u'CurrentType': u'current_type',
      u'CurrentVersion': u'current_version',
      u'PathName': u'path_name',
      u'ProductId': u'product_identifier',
      u'ProductName': u'product_name',
      u'RegisteredOrganization': u'registered_organization',
      u'RegisteredOwner': u'registered_owner',
      u'SystemRoot': u'system_root'}

  def _ParseInstallDate(self, registry_value):
    """Parses the InstallDate value.

    Args:
      registry_value (dfwinreg.WinRegistryValue): Windows Registry value.

    Returns:
      dfdatetime.DateTimeValues: installation date and time or None.
    """
    if not registry_value:
      return

    timestamp = registry_value.GetDataAsObject()
    if not timestamp:
      return dfdatetime_semantic_time.SemanticTime(string=u'Not set')

    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  def Collect(self, registry, output_writer):
    """Collects system information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the system information key was found, False if not.
    """
    current_version_key = registry.GetKeyByPath(
        self._CURRENT_VERSION_KEY_PATH)
    if not current_version_key:
      return False

    system_information = SystemInformation()

    for value_name, attribute_name in self._STRING_VALUES.items():
      value_string = self._GetValueAsStringFromKey(
          current_version_key, value_name)

      setattr(system_information, attribute_name, value_string)

    registry_value = current_version_key.GetValueByName(u'InstallDate')
    system_information.installation_date = self._ParseInstallDate(
        registry_value)

    output_writer.WriteSystemInformation(system_information)

    return True
