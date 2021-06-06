# -*- coding: utf-8 -*-
"""Catalog collector."""

import re


class CatalogCollector(object):
  """Catalog collector."""

  def _CollectCatalogDescriptors(self, registry_key, output_writer):
    """Collects the catalog descriptors from a Windows Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      output_writer (OutputWriter): output writer.
    """
    alphanumeric_compare = lambda key: [
        int(text) if text.isdigit() else text.lower()
        for text in re.split('([0-9]+)', key[0])]

    output_writer.WriteKeyPath(registry_key.path)
    value_descriptors = []
    for registry_value in registry_key.GetValues():
      value_descriptor = (
          registry_value.name or '', registry_value.data_type_string)
      value_descriptors.append(value_descriptor)

    for value_name, data_type_string in sorted(
          value_descriptors, key=alphanumeric_compare):
      output_writer.WriteValueDescriptor(
          value_name or '(default)', data_type_string)

    for sub_key in registry_key.GetSubkeys():
      self._CollectCatalogDescriptors(sub_key, output_writer)

  def Collect(self, root_key, output_writer):
    """Collects the catalog descriptors from a Windows Registry file.

    Args:
      root_key (dfwinreg.WinRegistryKey): root Windows Registry key.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the catalog could be collected, False if not.
    """
    self._CollectCatalogDescriptors(root_key, output_writer)
    return True
