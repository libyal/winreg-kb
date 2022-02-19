# -*- coding: utf-8 -*-
"""Catalog collector."""


class CatalogKeyDescriptor(object):
  """Catalog key descriptor.

  Attributes:
    key_path (str): path of Windows Registry key.
  """

  def __init__(self):
    """Initializes a catalog key descriptor."""
    super(CatalogKeyDescriptor, self).__init__()
    self.key_path = None
    self.value_descriptors = []


class CatalogCollector(object):
  """Catalog collector."""

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
      for key_descriptor in self._CollectCatalogKeyDescriptors(sub_key):
        yield key_descriptor

  def Collect(self, root_key):
    """Collects the catalog descriptors from a Windows Registry file.

    Args:
      root_key (dfwinreg.WinRegistryKey): root Windows Registry key.

    Yields:
      CatalogKeyDescriptor: catalog key descriptor.
    """
    for key_descriptor in self._CollectCatalogKeyDescriptors(root_key):
      yield key_descriptor
