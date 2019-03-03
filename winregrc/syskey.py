# -*- coding: utf-8 -*-
"""System key (syskey) collector."""

from __future__ import unicode_literals

import codecs

from winregrc import interface


class SystemKey(object):
  """System key.

  Attributes:
    boot_key (bytes): boot key.
  """

  def __init__(self):
    """Initializes a system key."""
    super(SystemKey, self).__init__()
    self.boot_key = None


class SystemKeyCollector(interface.WindowsRegistryKeyCollector):
  """System key collector.

  Attributes:
    system_key (SystemKey): system key.
  """

  _LSA_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Lsa')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a system key collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SystemKeyCollector, self).__init__(debug=debug)
    self._output_writer = output_writer
    self.system_key = None

  def _GetBootKey(self, registry):
    """Retrieves the boot key.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bytes: boot key or None if not found.
    """
    lsa_key = registry.GetKeyByPath(self._LSA_KEY_PATH)
    if not lsa_key:
      return None

    lsa_jd_key = lsa_key.GetSubkeyByName('JD')
    lsa_skew1_key = lsa_key.GetSubkeyByName('Skew1')
    lsa_gbg_key = lsa_key.GetSubkeyByName('GBG')
    lsa_data_key = lsa_key.GetSubkeyByName('Data')

    if None in (lsa_jd_key, lsa_skew1_key, lsa_gbg_key, lsa_data_key):
      return None

    lsa_jd_class_name = lsa_jd_key.class_name
    lsa_skew1_class_name = lsa_skew1_key.class_name
    lsa_gbg_class_name = lsa_gbg_key.class_name
    lsa_data_class_name = lsa_data_key.class_name

    if None in (
        lsa_jd_class_name, lsa_skew1_class_name, lsa_gbg_class_name,
        lsa_data_class_name):
      return None

    class_name_string = ''.join([
        lsa_jd_class_name, lsa_skew1_class_name, lsa_gbg_class_name,
        lsa_data_class_name])

    scrambled_key = codecs.decode(class_name_string, 'hex')
    key = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    for index, scrambled_index in enumerate([
        8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]):
      key[index] = scrambled_key[scrambled_index]

    return b''.join(key)

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects system information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the system key was found, False if not.
    """
    boot_key = self._GetBootKey(registry)
    if not boot_key:
      return False

    self.system_key = SystemKey()
    self.system_key.boot_key = boot_key

    return True
