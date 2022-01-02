# -*- coding: utf-8 -*-
"""Windows application identifiers (AppID) collector."""

from winregrc import interface


class ApplicationIdentifier(object):
  """Application identifier.

  Attributes:
    description (str): description.
    guid (str): identifier.
  """

  def __init__(self, guid, description):
    """Initializes an application identifier.

    Args:
      guid (str): identifier.
      description (str): description.
    """
    super(ApplicationIdentifier, self).__init__()
    self.description = description
    self.guid = guid


class ApplicationIdentifiersCollector(interface.WindowsRegistryKeyCollector):
  """Windows application identifiers collector."""

  _APPLICATION_IDENTIFIERS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Classes\\AppID')

  def _CollectApplicationIdentifiers(self, application_identifiers_key):
    """Collects Windows application identifiers (AppID).

    Args:
      application_identifiers_key (dfwinreg.WinRegistryKey): application
          identifiers Windows Registry key.

    Yields:
      ApplicationIdentifier: an application identifier.
    """
    for subkey in application_identifiers_key.GetSubkeys():
      name = subkey.name.lower()

      # Ignore subkeys that are not formatted as {%GUID%}
      if len(name) == 38 and name[0] == '{' and name[37] == '}':
        description = self._GetValueFromKey(subkey, '')

        yield ApplicationIdentifier(name, description)

  def Collect(self, registry):
    """Collects Windows application identifiers (AppID).

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      ApplicationIdentifier: an application identifier.
    """
    application_identifiers_key = registry.GetKeyByPath(
        self._APPLICATION_IDENTIFIERS_KEY_PATH)
    if application_identifiers_key:
      yield from self._CollectApplicationIdentifiers(
          application_identifiers_key)
