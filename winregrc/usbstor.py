# -*- coding: utf-8 -*-
"""Windows USB storage device collector."""

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import semantic_time as dfdatetime_semantic_time

from winregrc import data_format
from winregrc import errors


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


class USBStorageDeviceCollector(data_format.BinaryDataFormat):
  """Windows USB storage device collector."""

  _DEFINITION_FILE = 'usbstor.yaml'

  _USBSTOR_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Enum\\USBSTOR')

  def _CollectUSBStorageDevices(self, usbstor_key):
    """Collects USB storage devices.

    Args:
      usbstor_key (dfwinreg.WinRegistryKey): profile list Windows Registry key.

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

                storage_device_property.value_type = self._GetPropertyValueType(
                    property_value_key)
                storage_device_property.value = self._GetPropertyValueData(
                    property_value_key, storage_device_property.value_type)

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

  def _GetPropertyValueData(self, property_value_key, value_type):
    """Retrieves a property value data.

    Args:
      property_value_key (dfwinreg.WinRegistryKey): property value Windows
          Registry key.
      value_type (int): value type.

    Returns:
      object: property value data.

    Raises:
      ParseError: if the property value data cannot be determined.
    """
    binary_data = self._GetValueDataFromKey(property_value_key, 'Data')

    if value_type == 0x00000007:
      data_type_map = self._GetDataTypeMap('uint32le')
    elif value_type == 0x00000010:
      data_type_map = self._GetDataTypeMap('uint64le')
    elif value_type == 0x00000012:
      data_type_map = self._GetDataTypeMap('utf16le_string')
    else:
      raise errors.ParseError(f'Unsupported value type: 0x{value_type:08x}')

    try:
      value_data = self._ReadStructureFromByteStream(
          binary_data, 0, data_type_map, 'data')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          f'Unable to parse value: Data with error: {exception!s}')

    if value_type == 0x00000010:
      value_data = self._ParseFiletime(value_data)

    return value_data

  def _GetPropertyValueType(self, property_value_key):
    """Retrieves a property value type.

    Args:
      property_value_key (dfwinreg.WinRegistryKey): property value Windows
          Registry key.

    Returns:
      int: property value type.

    Raises:
      ParseError: if the property value type cannot be determined.
    """
    binary_data = self._GetValueDataFromKey(property_value_key, 'Type')

    data_type_map = self._GetDataTypeMap('uint32le')

    try:
      return self._ReadStructureFromByteStream(
          binary_data, 0, data_type_map, 'type')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          f'Unable to parse value: Type with error: {exception!s}')

  def _GetStringValueFromKey(
      self, registry_key, value_name, default_value=None):
    """Retrieves a string value from a Registry value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not registry_key:
      return default_value

    registry_value = registry_key.GetValueByName(value_name)
    if not registry_value:
      return default_value

    if not registry_value.DataIsString():
      return default_value

    return registry_value.GetDataAsObject()

  def _GetValueDataFromKey(self, registry_key, value_name):
    """Retrieves the value data from a Registry value.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.
      value_name (str): name of the value.

    Returns:
      bytes: value data or None if not available.
    """
    if not registry_key:
      return None

    registry_value = registry_key.GetValueByName(value_name)
    if not registry_value:
      return None

    return registry_value.data

  def _ParseFiletime(self, filetime):
    """Parses a FILETIME timestamp value.

    Args:
      filetime (int): a FILETIME timestamp value.

    Returns:
      dfdatetime.DateTimeValues: date and time values.
    """
    if filetime == 0:
      return dfdatetime_semantic_time.SemanticTime(string='Not set')

    if filetime == 0x7fffffffffffffff:
      return dfdatetime_semantic_time.SemanticTime(string='Never')

    return dfdatetime_filetime.Filetime(timestamp=filetime)

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
