#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import logging
import sys

import collector
import registry_file


# pylint: disable=superfluous-parens

class WindowsServicesCollector(collector.WindowsRegistryCollector):
  """Class that defines a Windows services collector."""

  def __init__(self):
    """Initializes the Windows services collector object."""
    super(WindowsServicesCollector, self).__init__()
    self.found_services_key = False

  def _CollectWindowsServicesFromKey(self, output_writer, services_key):
    """Collects the Windows services from a services Registry key.

    Args:
      output_writer: the output writer object.
      services_key: the services Registry key (instance of pyregf.key).
    """
    print(u'\tNumber of entries\t: {0:d}'.format(
        services_key.number_of_sub_keys))
    print(u'')

    for service_key in services_key.sub_keys:
      type_value = service_key.get_value_by_name(u'Type')
      if type_value:
        type_value = type_value.data_as_integer

      display_name_value = service_key.get_value_by_name(u'DisplayName')
      if display_name_value:
        if display_name_value.type in [
            registry_file.RegistryFile.REG_SZ,
            registry_file.RegistryFile.REG_EXPAND_SZ]:
          display_name_value = display_name_value.data_as_string
        else:
          display_name_value = None

      description_value = service_key.get_value_by_name(u'Description')
      if description_value:
        description_value = description_value.data_as_string

      image_path_value = service_key.get_value_by_name(u'ImagePath')
      if image_path_value:
        image_path_value = image_path_value.data_as_string

      object_name_value = service_key.get_value_by_name(u'ObjectName')
      if object_name_value:
        object_name_value = object_name_value.data_as_string

      start_value = service_key.get_value_by_name(u'Start')
      if start_value:
        start_value = start_value.data_as_integer

      windows_service = WindowsService(
          service_key.name, type_value, display_name_value, description_value,
          image_path_value, object_name_value, start_value)
      output_writer.WriteWindowsService(windows_service)

  def CollectWindowsServices(self, output_writer):
    """Collects the Windows services from the SYSTEM Registry file.

    Args:
      output_writer: the output writer object.
    """
    registry_file_object = self._OpenRegistryFile(
        self._REGISTRY_FILENAME_SYSTEM)

    root_key = registry_file_object.GetRootKey()

    if root_key:
      for control_set_key in root_key.sub_keys:
        if control_set_key.name.startswith(u'ControlSet'):
          services_key = control_set_key.get_sub_key_by_name(u'Services')
          if services_key:
            self.found_services_key = True

            print(u'Control set: {0:s}'.format(control_set_key.name))
            self._CollectWindowsServicesFromKey(output_writer, services_key)

    registry_file_object.Close()


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service: the Windows service (instance of WindowsService).
    """
    print(u'{0:s}'.format(service.name))

    if service.service_type:
      print(u'\tType\t\t\t: {0:s}'.format(service.GetServiceTypeDescription()))

    if service.display_name:
      print(u'\tDisplay name\t\t: {0:s}'.format(service.display_name))

    if service.description:
      print(u'\tDescription\t\t: {0:s}'.format(service.description))

    if service.image_path:
      print(u'\tExecutable\t\t: {0:s}'.format(service.image_path))

    if service.object_name:
      print(u'\t{0:s}\t\t: {1:s}'.format(
          service.GetObjectNameDescription(), service.object_name))

    if service.start_value is not None:
      print(u'\tStart\t\t\t: {0:s}'.format(service.GetStartValueDescription()))

    print(u'')


class WindowsService(object):
  """Class that defines a Windows service."""

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
      name: the name.
      service_type: the service type.
      display_name: the display name.
      description: the service description.
      image_path: the image path.
      object_name: the object name
      start_value: the start value.
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


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      u'Extract the services information from a SYSTEM Registry File (REGF).'))

  args_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SYSTEM Registry file.'))

  options = args_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    args_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = WindowsServicesCollector()

  if not collector_object.GetWindowsVolumePathSpec(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.CollectWindowsServices(output_writer)
  output_writer.Close()

  if not collector_object.found_services_key:
    print(u'No services key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
