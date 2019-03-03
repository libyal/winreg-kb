# -*- coding: utf-8 -*-
"""System information collector."""

from __future__ import unicode_literals

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
  """System information collector.

  Attributes:
    system_information (SystemInformation): system information.
  """

  _CURRENT_VERSION_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion')

  _STRING_VALUES = {
      'CSDVersion': 'csd_version',
      'CurrentBuildNumber': 'current_build_number',
      'CurrentType': 'current_type',
      'CurrentVersion': 'current_version',
      'PathName': 'path_name',
      'ProductId': 'product_identifier',
      'ProductName': 'product_name',
      'RegisteredOrganization': 'registered_organization',
      'RegisteredOwner': 'registered_owner',
      'SystemRoot': 'system_root'}

  def __init__(self, debug=False, output_writer=None):
    """Initializes a system information collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SystemInfoCollector, self).__init__(debug=debug)
    self._output_writer = output_writer
    self.system_information = None

  def _ParseInstallDate(self, registry_value):
    """Parses the InstallDate value.

    Args:
      registry_value (dfwinreg.WinRegistryValue): Windows Registry value.

    Returns:
      dfdatetime.PosixTime: installation date and time or None if not available.
    """
    if not registry_value:
      return None

    timestamp = registry_value.GetDataAsObject()
    if not timestamp:
      return dfdatetime_semantic_time.SemanticTime(string='Not set')

    return dfdatetime_posix_time.PosixTime(timestamp=timestamp)

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects system information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the system information key was found, False if not.
    """
    current_version_key = registry.GetKeyByPath(
        self._CURRENT_VERSION_KEY_PATH)
    if not current_version_key:
      return False

    self.system_information = SystemInformation()

    for value_name, attribute_name in self._STRING_VALUES.items():
      value_string = self._GetValueAsStringFromKey(
          current_version_key, value_name)

      setattr(self.system_information, attribute_name, value_string)

    registry_value = current_version_key.GetValueByName('InstallDate')
    self.system_information.installation_date = self._ParseInstallDate(
        registry_value)

    return True
