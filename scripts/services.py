#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import logging
import sys

from winreg_kb import services


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


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts the services information from a SYSTEM Registry File (REGF).'))

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SYSTEM Registry file.'))

  argument_parser.add_argument(
      u'--all', dest=u'all_control_sets', action=u'store_true', default=False,
      help=(
          u'Process all control sets instead of only the current control set.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = services.WindowsServicesCollector()

  if not collector_object.GetWindowsVolumePathSpec(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.Collect(
      output_writer, all_control_sets=options.all_control_sets)
  output_writer.Close()

  if not collector_object.found_services_key:
    print(u'No services key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
