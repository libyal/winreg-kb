#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract Application Compatibility Cache information."""

from __future__ import print_function
import argparse
import logging
import sys

from winregrc import appcompatcache
from winregrc import hexdump


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteDebugData(self, description, data):
    """Writes data for debugging.

    Args:
      description (str): description to write.
      data (bytes): data to write.
    """
    print(description.encode(u'utf8'))
    print(hexdump.Hexdump(data))

  def WriteDebugValue(self, description, value):
    """Writes a value for debugging.

    Args:
      description (str): description to write.
      value (str): value to write.
    """
    alignment = 8 - (len(description) / 8)

    text = u'{0:s}{1:s}{2:s}'.format(description, u'\t' * alignment, value)
    print(text.encode(u'utf8'))

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text (bytes): text to write.
    """
    print(text)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts Application Compatibility Cache information from '
      u'a SYSTEM Registry file.'))

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

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  collector_object = appcompatcache.AppCompatCacheCollector(
      debug=options.debug)

  if not collector_object.ScanForWindowsVolume(options.source):
    print((
        u'Unable to retrieve the volume with the Windows directory from: '
        u'{0:s}.').format(options.source))
    print(u'')
    return False

  collector_object.Collect(output_writer)
  output_writer.Close()

  if not collector_object.key_found:
    print(u'No Application Compatibility Cache key found.')

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
