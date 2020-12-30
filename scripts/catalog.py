#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract a catalog of Windows Registry keys and values."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from winregrc import catalog
from winregrc import output_writers


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts a catalog of Windows Registry keys and values.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help='path of a Windows Registry file.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  collector_object = catalog.CatalogCollector()

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No shell folder identifier keys found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
