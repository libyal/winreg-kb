#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to extract Security Account Manager (SAM) information."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import logging
import sys

from dfdatetime import filetime as dfdatetime_filetime

from winregrc import collector
from winregrc import output_writer
from winregrc import sam


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Stdout output writer."""

  def _WriteFiletimeValue(self, description, value):
    """Writes a FILETIME timestamp value.

    Args:
      description (str): description to write.
      value (str): value to write.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    elif value == 0x7fffffffffffffff:
      date_time_string = 'Never'
    else:
      date_time = dfdatetime_filetime.Filetime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()

    self.WriteValue(description, date_time_string)

  def WriteText(self, text):
    """Writes text to stdout.

    Args:
      text (bytes): text to write.
    """
    print(text)

  def WriteUserAccount(self, user_account):
    """Writes an user account to stdout.

    Args:
      user_account (UserAccount): user account to write.
    """
    self.WriteValue('Username', user_account.username)
    self.WriteValue('Relative identifier (RID)', user_account.rid)
    self.WriteValue('Primary group identifier', user_account.primary_gid)

    if user_account.full_name:
      self.WriteValue('Full name', user_account.full_name)

    if user_account.comment:
      self.WriteValue('Comment', user_account.comment)

    if user_account.user_comment:
      self.WriteValue('User comment', user_account.user_comment)

    self._WriteFiletimeValue('Last log-in time', user_account.last_login_time)

    self._WriteFiletimeValue(
        'Last password set time', user_account.last_password_set_time)

    self._WriteFiletimeValue(
        'Account expiration time', user_account.account_expiration_time)

    self._WriteFiletimeValue(
        'Last password failure time', user_account.last_password_failure_time)

    self.WriteValue('Number of log-ons', user_account.number_of_logons)
    self.WriteValue(
        'Number of password failures',
        user_account.number_of_password_failures)

    if user_account.codepage:
      self.WriteValue('Codepage', user_account.codepage)

    self.WriteText('')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Extracts Security Account Manager information from a SAM Registry '
      'file.'))

  argument_parser.add_argument(
      '-d', '--debug', dest='debug', action='store_true', default=False,
      help='enable debug output.')

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='PATH', default=None,
      help=(
          'path of the volume containing C:\\Windows, the filename of '
          'a storage media image containing the C:\\Windows directory,'
          'or the path of a SAM Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer_object = StdoutWriter()

  if not output_writer_object.Open():
    print('Unable to open output writer.')
    print('')
    return False

  registry_collector = collector.WindowsRegistryCollector()
  if not registry_collector.ScanForWindowsVolume(options.source):
    print('Unable to retrieve the Windows Registry from: {0:s}.'.format(
        options.source))
    print('')
    return False

  # TODO: map collector to available Registry keys.
  collector_object = sam.SecurityAccountManagerCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print('No Security Account Manager key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
