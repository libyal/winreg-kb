# -*- coding: utf-8 -*-
"""Security Account Manager (SAM) collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfwinreg import registry

from winreg_kb import collector
from winreg_kb import hexdump


# pylint: disable=logging-format-interpolation

class SecurityAccountManagerCollector(collector.WindowsVolumeCollector):
  """Class that defines a Security Account Manager (SAM) collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

  def __init__(self, debug=False, mediator=None):
    """Initializes a Security Account Manager (SAM) collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(SecurityAccountManagerCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  # Bytes 8-15 represent the last login date for the account.
  # Bytes 24-31 represent the date that the password was last reset (if the password hasn’t been reset or changed, this date will correlate to the account creation date).
  # Bytes 32-39 represent the account expiration date.
  # Bytes 40-47 represent the date of the last failed login attempt (because the account name has to be correct for the date to be changed on a specific account, this date can also be referred to as the date of the last incorrect password usage).

  def Collect(self, output_writer):
    """Collects the Security Account Manager.

    Args:
      output_writer (OutputWriter): output writer.
    """
    self.key_found = False

    users_path = u'HKEY_LOCAL_MACHINE\\SAM\\Domains\\Account\\Users'
    # TODO: iterate subkeys
    # TODO: self._CollectUserFromKey(output_writer, key_path)
    # TODO: get date time values form F value
    # TODO: read V value
