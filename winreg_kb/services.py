# -*- coding: utf-8 -*-
"""Windows services collector."""

from __future__ import print_function

from dfwinreg import registry

from winreg_kb import collector


class WindowsService(object):
  """Class that defines a Windows service.

  Attributes:
    description: string containing the service description.
    display_name: string containing the display name.
    image_path: string containing the image path.
    name: string containing the name.
    object_name: string containing the object name
    service_type: string containing the service type.
    start_value: string containing the start value.
  """

  _OBJECT_NAME_DESCRIPTIONS = {
      0x00000010: u'Account name',
      0x00000020: u'Account name',
      0x00000110: u'Account name',
  }

  _SERVICE_TYPE_DESCRIPTIONS = {
      0x00000001: u'Kernel device driver',
      0x00000002: u'File system driver',
      0x00000004: u'Adapter arguments',
      0x00000010: u'Stand-alone service',
      0x00000020: u'Shared service',
  }

  _START_VALUE_DESCRIPTIONS = {
      0x00000000: u'Boot',
      0x00000001: u'System',
      0x00000002: u'Automatic',
      0x00000003: u'On demand',
      0x00000004: u'Disabled',
  }

  def __init__(
      self, name, service_type, display_name, description, image_path,
      object_name, start_value):
    """Initializes the Windows service object.

    Args:
      name: string containing the name.
      service_type: string containing the service type.
      display_name: string containing the display name.
      description: string containing the service description.
      image_path: string containing the image path.
      object_name: string containing the object name
      start_value: string containing the start value.
    """
    super(WindowsService, self).__init__()
    self.description = description
    self.display_name = display_name
    self.image_path = image_path
    self.name = name
    self.object_name = object_name
    self.service_type = service_type
    self.start_value = start_value

  def GetObjectNameDescription(self):
    """Retrieves the object name as a descriptive string."""
    return(self._OBJECT_NAME_DESCRIPTIONS.get(
        self.service_type, u'Object name'))

  def GetServiceTypeDescription(self):
    """Retrieves the service type as a descriptive string."""
    return(self._SERVICE_TYPE_DESCRIPTIONS.get(
        self.service_type, u'Unknown 0x{0:08x}'.format(self.service_type)))

  def GetStartValueDescription(self):
    """Retrieves the start value as a descriptive string."""
    return(self._START_VALUE_DESCRIPTIONS.get(
        self.start_value, u'Unknown 0x{0:08x}'.format(self.start_value)))


class WindowsServicesCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows services collector.

  Attributes:
    found_services_key: boolean value to indicate the Services
                        Registry key was found.
  """

  def __init__(self):
    """Initializes the collector object."""
    super(WindowsServicesCollector, self).__init__()
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.found_services_key = False

  def _CollectWindowsServicesFromKey(self, output_writer, services_key):
    """Collects the Windows services from a services Registry key.

    Args:
      output_writer: the output writer object.
      services_key: the services Registry key (instance of pyregf.key).
    """
    print(u'\tNumber of entries\t: {0:d}'.format(
        services_key.number_of_subkeys))
    print(u'')

    for service_key in services_key.GetSubkeys():
      type_value = service_key.GetValueByName(u'Type')
      if type_value:
        type_value = type_value.GetDataAsObject()

      display_name_value = service_key.GetValueByName(u'DisplayName')
      if display_name_value:
        if display_name_value.DataIsString():
          display_name_value = display_name_value.GetDataAsObject()
        else:
          display_name_value = None

      description_value = service_key.GetValueByName(u'Description')
      if description_value:
        description_value = description_value.GetDataAsObject()

      image_path_value = service_key.GetValueByName(u'ImagePath')
      if image_path_value:
        image_path_value = image_path_value.GetDataAsObject()

      object_name_value = service_key.GetValueByName(u'ObjectName')
      if object_name_value:
        object_name_value = object_name_value.GetDataAsObject()

      start_value = service_key.GetValueByName(u'Start')
      if start_value:
        start_value = start_value.GetDataAsObject()

      windows_service = WindowsService(
          service_key.name, type_value, display_name_value, description_value,
          image_path_value, object_name_value, start_value)
      output_writer.WriteWindowsService(windows_service)

  def Collect(self, output_writer, all_control_sets=False):
    """Collects the services.

    Args:
      output_writer: the output writer object.
      all_control_sets: optional value to indicate that services should be
                        collected from all control sets instead of only the
                        current control set. The default is false.
    """
    self.found_services_key = False

    if all_control_sets:
      system_key = self._registry.GetKeyByPath(u'HKEY_LOCAL_MACHINE\\System\\')
      if not system_key:
        return

      for control_set_key in system_key.GetSubkeys():
        if control_set_key.name.startswith(u'ControlSet'):
          services_key = control_set_key.GetSubkeyByName(u'Services')
          if services_key:
            self.found_services_key = True

            print(u'Control set: {0:s}'.format(control_set_key.name))
            self._CollectWindowsServicesFromKey(output_writer, services_key)

    else:
      services_key = self._registry.GetKeyByPath(
          u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services')
      if services_key:
        self.found_services_key = True

        print(u'Current control set')
        self._CollectWindowsServicesFromKey(output_writer, services_key)
