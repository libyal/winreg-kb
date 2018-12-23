# -*- coding: utf-8 -*-
"""Windows application identifiers (AppID) collector."""

from __future__ import unicode_literals

from winregrc import interface


class ApplicationIdentifier(object):
  """Application identifier

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

  def Collect(self, registry, output_writer):
    """Collects the application identifiers.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the application identifiers key was found, False if not.
    """
    application_identifiers_key = registry.GetKeyByPath(
        self._APPLICATION_IDENTIFIERS_KEY_PATH)
    if not application_identifiers_key:
      return False

    for subkey in application_identifiers_key.GetSubkeys():
      guid = subkey.name.lower()

      # Ignore subkeys that are not formatted as {%GUID%}
      if len(guid) != 38 and guid[0] == '{' and guid[37] == '}':
        continue

      description = self._GetValueAsStringFromKey(subkey, '')

      application_identifier = ApplicationIdentifier(
          guid, description)
      output_writer.WriteApplicationIdentifier(application_identifier)

    return True
