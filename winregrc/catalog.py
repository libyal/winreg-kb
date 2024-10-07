# -*- coding: utf-8 -*-
"""Catalog collector."""

import re


class CatalogKeyDescriptor(object):
  """Catalog key descriptor.

  Attributes:
    grouped_key_paths (list[str]): paths of Windows Registry keys with similar
        values.
    key_path (str): path of Windows Registry key.
    value_descriptors (tuple[str,str]): pairs of value name and data type.
  """

  def __init__(self):
    """Initializes a catalog key descriptor."""
    super(CatalogKeyDescriptor, self).__init__()
    self.grouped_key_paths = []
    self.key_path = None
    self.value_descriptors = []


class CatalogCollector(object):
  """Catalog collector."""

  def __init__(self, group_keys=False):
    """Initializes a catalog collector.

    Args:
      group_keys (bool): group keys with similar values.
    """
    super(CatalogCollector, self).__init__()
    self._group_keys = group_keys

  def _CollectCatalogKeyDescriptors(self, registry_key):
    """Collects the catalog key descriptors from a Windows Registry key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Yields:
      CatalogKeyDescriptor: catalog key descriptor.
    """
    key_descriptor = CatalogKeyDescriptor()
    key_descriptor.key_path = registry_key.path

    for registry_value in registry_key.GetValues():
      value_descriptor = (
          registry_value.name or '(default)', registry_value.data_type_string)
      key_descriptor.value_descriptors.append(value_descriptor)

    yield key_descriptor

    for sub_key in registry_key.GetSubkeys():
      yield from self._CollectCatalogKeyDescriptors(sub_key)

  def Collect(self, root_key):
    """Collects the catalog descriptors from a Windows Registry file.

    Args:
      root_key (dfwinreg.WinRegistryKey): root Windows Registry key.

    Yields:
      CatalogKeyDescriptor: catalog key descriptor.
    """
    if not self._group_keys:
      yield from self._CollectCatalogKeyDescriptors(root_key)

    else:
      def AlphanumericCompare(key):
        return (int(text) if text.isdigit() else text.lower()
                for text in re.split('([0-9]+)', key[0]))

      key_descriptors_per_value_hash = {}

      for key_descriptor in self._CollectCatalogKeyDescriptors(root_key):
        values_hash = hash('\n'.join([
            '\t'.join([value_name, data_type_string])
            for value_name, data_type_string in sorted(
                key_descriptor.value_descriptors, key=AlphanumericCompare)]))

        matching_key_descriptor = key_descriptors_per_value_hash.get(
            values_hash, None)
        if matching_key_descriptor:
          matching_key_descriptor.grouped_key_paths.append(
              key_descriptor.key_path)
        else:
          key_descriptors_per_value_hash[values_hash] = key_descriptor

      yield from key_descriptors_per_value_hash.values()
