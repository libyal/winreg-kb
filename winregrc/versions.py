# -*- coding: utf-8 -*-
"""Windows versions."""


class WindowsVersions(object):
  """Windows versions."""

  _SORT_KEY_PER_VERSION = {
       # TODO: update the dates of the Windows 10 releases.
      'Windows 10 (1511)': 2015,
      'Windows 10 (1607)': 2015,
      'Windows 10 (1703)': 2015,
      'Windows 10 (1709)': 2015,
      'Windows 10 (1803)': 2015,
      'Windows 10 (1809)': 2015,
      'Windows 10 (1903)': 2015,
      'Windows 10 (1909)': 2015,
      'Windows 10 (2004)': 2015,
      'Windows 10 (20H2)': 2015,
      'Windows 11 (21H2)': 2021,
      'Windows 2000': 2000,
      'Windows 2003': 2003,
      'Windows 2003 R2': 2005,
      'Windows 2008': 2008,
      'Windows 2008 R2': 2009,
      'Windows 2012': 2012,
      'Windows 2012 R2': 2013,
      'Windows 2016': 2016,
      'Windows 2019': 2019,
      'Windows 7': 2009,
      'Windows 8.0': 2012,
      'Windows 8.1': 2013,
      'Windows 95': 1995,
      'Windows 98': 1998,
      'Windows Me': 2000,
      'Windows NT4': 1996,
      'Windows Vista': 2007,
      'Windows XP 32-bit': 2001,
      'Windows XP 64-bit': 2005}

  @classmethod
  def KeyFunction(cls, windows_version):
    """Key function for sorting.

    Args:
      windows_version (str): Windows version.

    Returns:
      tuple[int, str]: sort key and Windows version
    """
    sort_key = cls._SORT_KEY_PER_VERSION.get(windows_version, 9999)
    return sort_key, windows_version
