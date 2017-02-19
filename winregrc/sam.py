# -*- coding: utf-8 -*-
"""Security Account Manager (SAM) collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfwinreg import registry

from winregrc import hexdump
from winregrc import interface


# pylint: disable=logging-format-interpolation

class SecurityAccountManagerCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a Security Account Manager (SAM) collector."""

  # Bytes 8-15 represent the last login date for the account.
  # Bytes 24-31 represent the date that the password was last reset (if the password hasn’t been reset or changed, this date will correlate to the account creation date).
  # Bytes 32-39 represent the account expiration date.
  # Bytes 40-47 represent the date of the last failed login attempt (because the account name has to be correct for the date to be changed on a specific account, this date can also be referred to as the date of the last incorrect password usage).

  def Collect(self, registry, output_writer):
    """Collects the Security Account Manager (SAM) information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Security Account Manager (SAM) information key was found,
          False if not.
    """
    users_path = u'HKEY_LOCAL_MACHINE\\SAM\\Domains\\Account\\Users'
    # TODO: iterate subkeys
    # TODO: self._CollectUserFromKey(output_writer, key_path)
    # TODO: get date time values form F value
    # TODO: read V value

    return True
