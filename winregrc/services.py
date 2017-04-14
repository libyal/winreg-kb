# -*- coding: utf-8 -*-
"""Windows services collector."""

from __future__ import print_function

from winregrc import interface


class WindowsService(object):
  """Windows service.

  Attributes:
    description (str): service description.
    display_name (str): display name.
    image_path (str): image path.
    name (str): name.
    object_name (str): object name
    service_type (str): service type.
    start_value (str): start value.
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
    """Initializes a Windows service.

    Args:
      name (str): name.
      service_type (str): service type.
      display_name (str): display name.
      description (str): service description.
      image_path (str): image path.
      object_name (str): object name
      start_value (str): start value.
    """
    super(WindowsService, self).__init__()
    self.description = description
    self.display_name = display_name
    self.image_path = image_path
    self.name = name
    self.object_name = object_name
    self.service_type = service_type
    self.start_value = start_value

  def __eq__(self, other):
    """Determines the current Windows service is equal to the other.

    Returns:
      bool: True if equal.
    """
    return (
        other is not None and
        self.description == other.description and
        self.display_name == other.display_name and
        self.image_path == other.image_path and
        self.name == other.name and
        self.object_name == other.object_name and
        self.service_type == other.service_type and
        self.start_value == other.start_value)

  def __ne__(self, other):
    """Determines the current Windows service is not equal to the other.

    Returns:
      bool: True if not equal.
    """
    return (
        other is None or
        self.description != other.description or
        self.display_name != other.display_name or
        self.image_path != other.image_path or
        self.name != other.name or
        self.object_name != other.object_name or
        self.service_type != other.service_type or
        self.start_value != other.start_value)

  def GetObjectNameDescription(self):
    """Retrieves the object name description.

    Return:
      str: object name description.
    """
    return(self._OBJECT_NAME_DESCRIPTIONS.get(
        self.service_type, u'Object name'))

  def GetServiceTypeDescription(self):
    """Retrieves the service type description.

    Return:
      str: service type description.
    """
    return(self._SERVICE_TYPE_DESCRIPTIONS.get(
        self.service_type, u'Unknown 0x{0:08x}'.format(self.service_type)))

  def GetStartValueDescription(self):
    """Retrieves the start value description.

    Return:
      str: start value description.
    """
    return(self._START_VALUE_DESCRIPTIONS.get(
        self.start_value, u'Unknown 0x{0:08x}'.format(self.start_value)))


class WindowsServicesCollector(interface.WindowsRegistryKeyCollector):
  """Windows services collector."""

  def _CollectWindowsServicesFromKey(self, services_key):
    """Collects the Windows services from a services Registry key.

    Args:
      services_key (dfwinreg.WinRegistryKey): services Registry key.

    Yields:
      WindowsService: Windows service.
    """
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

      yield WindowsService(
          service_key.name, type_value, display_name_value, description_value,
          image_path_value, object_name_value, start_value)

  # pylint: disable=arguments-differ
  def Collect(self, registry, output_writer, all_control_sets=False):
    """Collects the services.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.
      all_control_sets (Optional[bool]): True if the services should be
          collected from all control sets instead of only the current control
          set.

    Returns:
      bool: True if the services key was found, False if not.
    """
    result = False

    if all_control_sets:
      system_key = registry.GetKeyByPath(u'HKEY_LOCAL_MACHINE\\System\\')
      if not system_key:
        return result

      for control_set_key in system_key.GetSubkeys():
        if control_set_key.name.startswith(u'ControlSet'):
          services_key = control_set_key.GetSubkeyByName(u'Services')
          if services_key:
            result = True

            if self._debug:
              print(u'Control set: {0:s}'.format(control_set_key.name))
              print(u'\tNumber of entries\t: {0:d}'.format(
                  services_key.number_of_subkeys))
              print(u'')

            for windows_service in self._CollectWindowsServicesFromKey(
                services_key):
              output_writer.WriteWindowsService(windows_service)

    else:
      services_key = registry.GetKeyByPath(
          u'HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Services')
      if services_key:
        result = True

        if self._debug:
          print(u'Current control set')
          print(u'\tNumber of entries\t: {0:d}'.format(
              services_key.number_of_subkeys))
          print(u'')

        for windows_service in self._CollectWindowsServicesFromKey(
            services_key):
          output_writer.WriteWindowsService(windows_service)

    return result

  def Compare(self, registry, output_writer):
    """Compares services in the different control sets.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the services key was found, False if not.
    """
    system_key = registry.GetKeyByPath(u'HKEY_LOCAL_MACHINE\\System\\')
    if not system_key:
      return False

    result = False
    control_sets = []
    service_names = set()
    for control_set_key in system_key.GetSubkeys():
      if control_set_key.name.startswith(u'ControlSet'):
        services_key = control_set_key.GetSubkeyByName(u'Services')
        if not services_key:
          continue

        result = True

        services = {}
        for windows_service in self._CollectWindowsServicesFromKey(
            services_key):
          if windows_service.name in services:
            # TODO: print warning.
            continue

          windows_service_name = windows_service.name.lower()
          service_names.add(windows_service_name)
          services[windows_service_name] = windows_service

        control_sets.append(services)

    number_of_control_sets = len(control_sets)
    for name in service_names:
      services_diff = set()

      windows_service = control_sets[0].get(name, None)
      for control_set_index in range(1, number_of_control_sets):
        control_set = control_sets[control_set_index]

        compare_windows_service = control_set.get(name, None)
        if windows_service != compare_windows_service:
          services_diff.add(windows_service)
          services_diff.add(compare_windows_service)

      for windows_service in services_diff:
        if not windows_service:
          if self._debug:
            print(u'Not defined')
        else:
          output_writer.WriteWindowsService(windows_service)

    return result
