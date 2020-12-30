# -*- coding: utf-8 -*-
"""Catalog collector."""

from dfwinreg import creg as dfwinreg_creg
from dfwinreg import regf as dfwinreg_regf


class CatalogCollector(object):
  """Catalog collector."""

  def _CollectCatalogDescriptors(self, registry_key):
    """Collects the catalog descriptors from a Windows Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
    """
    for registry_value in registry_key.GetValues():
      print(registry_key.key_path, registry_value.name, registry_value.data_type_string)

    for sub_key in registry_key.GetSubKeys():
      self._CollectCatalogDescriptors(sub_key)

  def Collect(self, path, output_writer):
    """Collects the catalog descriptors from a Windows Registry file.

    Args:
      path (str): path to Windows Registry file.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if a root key was found, False if not.
    """
    with open(options.source, 'rb') as file_object:
      try:
        registry_file = dfwinreg_regf.REGFWinRegistryFile()

        registry_file.Open(file_object)
      except IOError:
        registry_file = None

      if not registry_file:
        try:
          registry_file = dfwinreg_creg.CREGWinRegistryFile()

          registry_file.Open(file_object)
        except IOError:
          registry_file = None

      if not registry_file:
        return False

      root_key = registry_file.GetRootKey()
      if not root_key:
        return False

      return True
