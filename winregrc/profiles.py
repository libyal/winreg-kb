# -*- coding: utf-8 -*-
"""Windows user profiles collector."""

from winregrc import interface


class UserProfilesCollector(interface.WindowsRegistryKeyCollector):
  """Windows user profiles collector."""

  _PROFILE_LIST_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      u'ProfileList')

  def Collect(self, registry, output_writer):
    """Collects the user profiles.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the user profile key was found, False if not.
    """
    profile_list_key = registry.GetKeyByPath(
        self._PROFILE_LIST_KEY_PATH)
    if not profile_list_key:
      return False

    for subkey in profile_list_key.GetSubkeys():
      profile_image_path = self._GetValueAsStringFromKey(
          subkey, u'ProfileImagePath')

      output_writer.WriteText(u'{0:s}: {1:s}'.format(
          subkey.name, profile_image_path))

    return True
