#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract services information."""

from __future__ import print_function
import argparse
import logging
import sys

from winregrc import collector
from winregrc import output_writer
from winregrc import services


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def __init__(self, use_tsv=False):
    """Initializes a stdout output writer.

    Args:
      use_tsv (bool): True if the output should in tab separated values.
    """
    super(StdoutWriter, self).__init__()
    self._printed_header = False
    self._use_tsv = use_tsv

  def WriteWindowsService(self, service):
    """Writes the Windows service to stdout.

    Args:
      service (WindowsService): Windows service.
    """
    service_type_description = u''
    if service.service_type:
      service_type_description = service.GetServiceTypeDescription()

    start_value_description = u''
    if service.start_value is not None:
      start_value_description = service.GetStartValueDescription()

    if self._use_tsv:
      if not self._printed_header:
        print(u'Service\tType\tDisplay name\tDescription\tExecutable\tStart')
        self._printed_header = True

      service_display_name = service.display_name or u''
      service_description = service.description or u''
      service_image_path = service.image_path or u''

      print(u'{0:s}\t{1:s}\t{2:s}\t{3:s}\t{4:s}\t{5:s}'.format(
          service.name, service_type_description, service_display_name,
          service_description, service_image_path, start_value_description))

    else:
      print(u'{0:s}'.format(service.name))

      if service.service_type:
        print(u'\tType\t\t\t: {0:s}'.format(service_type_description))

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
        print(u'\tStart\t\t\t: {0:s}'.format(start_value_description))

      print(u'')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts the services information from a SYSTEM Registry file.'))

  argument_parser.add_argument(
      u'--all', dest=u'all_control_sets', action=u'store_true', default=False,
      help=(
          u'Process all control sets instead of only the current control set.'))

  argument_parser.add_argument(
      u'--diff', dest=u'diff_control_sets', action=u'store_true', default=False,
      help=u'Only list differences between control sets.')

  argument_parser.add_argument(
      u'--tsv', dest=u'use_tsv', action=u'store_true', default=False,
      help=u'Use tab separated value (TSV) output.')

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SYSTEM Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer_object = StdoutWriter(use_tsv=options.use_tsv)

  if not output_writer_object.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print(u'Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print(u'')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = services.WindowsServicesCollector(
      debug=options.debug)

  if options.diff_control_sets:
    result = collector_object.Compare(
        registry_collector.registry, output_writer_object)
  else:
    result = collector_object.Collect(
        registry_collector.registry, output_writer_object,
        all_control_sets=options.all_control_sets)

  if not result:
    print(u'No Services key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
