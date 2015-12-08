# -*- coding: utf-8 -*-
"""Windows user profiles collector."""

from dfwinreg import registry

from winreg_kb import collector


class UserProfilesCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows user profiles collector.

  Attributes:
    found_app_compat_cache_key: boolean value to indicate the Profile List
                                Registry key was found.
  """

  DEFAULT_VALUE_NAME = u''

  _PROFILE_LIST_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      u'ProfileList')

  def __init__(self):
    """Initializes the collector object."""
    super(UserProfilesCollector, self).__init__()
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.found_profile_list_key = False

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

    value = key.GetValueByName(value_name)
    if not value:
      return default_value

    return value.GetDataAsObject()

  def Collect(self, output_writer):
    """Collects the system information.

    Args:
      output_writer: the output writer object.
    """
    self.found_profile_list_key = False

    profile_list_key = self._registry.GetKeyByPath(
        self._PROFILE_LIST_KEY_PATH)
    if not profile_list_key:
      return

    self.found_profile_list_key = True

    for sub_key in profile_list_key.GetSubkeys():
      profile_image_path = self._GetValueAsStringFromKey(
          sub_key, u'ProfileImagePath')

      output_writer.WriteText(u'{0:s}: {1:s}'.format(
          sub_key.name, profile_image_path))
