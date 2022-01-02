# -*- coding: utf-8 -*-
"""Windows user profiles collector."""

from winregrc import interface


class UserProfile(object):
  """User profile.

  Attributes:
    profile_path (str): path of the users profile.
    security_identifier (str): security identifier of the user.
  """

  def __init__(self, security_identifier, profile_path):
    """Initializes an user profile.

    Args:
      security_identifier (str): security identifier of the user.
      profile_path (str): path of the users profile.
    """
    super(UserProfile, self).__init__()
    self.profile_path = profile_path
    self.security_identifier = security_identifier


class UserProfilesCollector(interface.WindowsRegistryKeyCollector):
  """Windows user profiles collector."""

  _PROFILE_LIST_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      'ProfileList')

  def _CollectUserProfiles(self, profile_list_key):
    """Collects user profiles.

    Args:
      profile_list_key (dfwinreg.WinRegistryKey): profile list Windows Registry.

    Yields:
      UserProfile: an user profile.
    """
    for subkey in profile_list_key.GetSubkeys():
      profile_image_path = self._GetValueFromKey(subkey, 'ProfileImagePath')

      yield UserProfile(subkey.name, profile_image_path)

  def Collect(self, registry):
    """Collects user profiles.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      UserProfile: an user profile.
    """
    profile_list_key = registry.GetKeyByPath(self._PROFILE_LIST_KEY_PATH)
    if profile_list_key:
      yield from self._CollectUserProfiles(profile_list_key)
