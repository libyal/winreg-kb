# -*- coding: utf-8 -*-
"""Windows USB storage device collector."""

from winregrc import interface


class USBStorageDeviceProperty(object):
  """USB storage device property.

  Attributes:
    identifier (str): identifier of the property.
    property_set (str): identifier of the property set.
    value (object): property value.
    value_type (int): property value type.
  """

  def __init__(self, property_set, identifier):
    """Initializes an USB storage device property.

    Args:
      property_set (str): identifier of the property set.
      identifier (str): identifier of the property.
    """
    super(USBStorageDeviceProperty, self).__init__()
    self.identifier = identifier
    self.property_set = property_set
    self.value = None
    self.value_type = None


class USBStorageDevice(object):
  """USB storage device.

  Attributes:
    device_type (str): type of USB device.
    display_name (str): display name of the USB device.
    key_path (str): Windows Registry key path.
    product (str): product of the USB device.
    properties (list[USBStorageDeviceProperty]): properties.
    revision (str): revision number of the USB device.
    vendor (str): vendor of the USB device.
  """

  def __init__(self):
    """Initializes an USB storage device."""
    super(USBStorageDevice, self).__init__()
    self.device_type = None
    self.display_name = None
    self.key_path = None
    self.product = None
    self.properties = []
    self.revision = None
    self.vendor = None


class USBStorageDeviceCollector(interface.WindowsRegistryKeyCollector):
  """Windows USB storage device collector."""

  _USBSTOR_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Enum\\USBSTOR')

  def _CollectUSBStorageDevices(self, usbstor_key):
    """Collects USB storage devices.

    Args:
      usbstor_key (dfwinreg.WinRegistryKey): profile list Windows Registry.

    Yields:
      USBStorageDevice: an USB storage device.
    """
    for device_key in usbstor_key.GetSubkeys():
      name_values = device_key.name.split('&')
      device_type = None
      product = None
      revision = None
      vendor = None

      number_of_name_values = len(name_values)
      if number_of_name_values >= 1:
        device_type = name_values[0]
      if number_of_name_values >= 2:
        vendor = name_values[1]
      if number_of_name_values >= 3:
        product = name_values[2]
      if number_of_name_values >= 4:
        revision = name_values[3]

      for device_instance_key in device_key.GetSubkeys():
        properties = []
        properties_key = device_instance_key.GetSubkeyByName('Properties')
        if properties_key:
          for property_set_key in properties_key.GetSubkeys():
            for property_key in property_set_key.GetSubkeys():
              for property_value_key in property_key.GetSubkeys():
                storage_device_property = USBStorageDeviceProperty(
                    property_set_key.name, property_key.name)

                # TODO: store value in storage_device_property.
                _ = property_value_key

                properties.append(storage_device_property)

        storage_device = USBStorageDevice()
        storage_device.device_type = device_type
        storage_device.display_name = self._GetStringValueFromKey(
            device_instance_key, 'FriendlyName')
        storage_device.key_path = device_instance_key.path
        storage_device.product = product
        storage_device.properties = properties
        storage_device.revision = revision
        storage_device.vendor = vendor

      yield storage_device

  def Collect(self, registry):
    """Collects USB storage devices.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Yields:
      USBStorageDevice: an USB storage device.
    """
    usbstor_key = registry.GetKeyByPath(self._USBSTOR_KEY_PATH)
    if usbstor_key:
      yield from self._CollectUSBStorageDevices(usbstor_key)
