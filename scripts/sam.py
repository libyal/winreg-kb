#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to extract Security Account Manager (SAM) information."""

from __future__ import print_function
import argparse
import logging
import sys

from winregrc import collector
from winregrc import output_writer
from winregrc import sam


class StdoutWriter(output_writer.StdoutOutputWriter):
  """Class that defines a stdout output writer."""

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
    self.WriteValue(u'Username', user_account.username)
    self.WriteValue(u'Relative identifier (RID)', user_account.rid)
    self.WriteValue(u'Primary group identifier', user_account.primary_gid)

    if user_account.full_name:
      self.WriteValue(u'Full name', user_account.full_name)

    if user_account.comment:
      self.WriteValue(u'Comment', user_account.comment)

    if user_account.user_comment:
      self.WriteValue(u'User comment', user_account.user_comment)

    # TODO: convert to date time string.
    self.WriteValue(u'Last log-in time', user_account.last_login_time)
    self.WriteValue(
        u'Last password set time', user_account.last_password_set_time)
    self.WriteValue(
        u'Account expiration time', user_account.account_expiration_time)
    self.WriteValue(
        u'Last password failure time', user_account.last_password_failure_time)

    self.WriteValue(u'Number of log-ons', user_account.number_of_logons)
    self.WriteValue(
        u'Number of password failures',
        user_account.number_of_password_failures)

    if user_account.codepage:
      self.WriteValue(u'Codepage', user_account.codepage)

    self.WriteText(u'')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Extracts Security Account Manager information from a SAM Registry '
      u'file.'))

  argument_parser.add_argument(
      u'-d', u'--debug', dest=u'debug', action=u'store_true', default=False,
      help=u'enable debug output.')

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'PATH', default=None,
      help=(
          u'path of the volume containing C:\\Windows, the filename of '
          u'a storage media image containing the C:\\Windows directory,'
          u'or the path of a SAM Registry file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer_object = StdoutWriter()

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
  collector_object = sam.SecurityAccountManagerCollector(
      debug=options.debug)

  result = collector_object.Collect(
      registry_collector.registry, output_writer_object)
  if not result:
    print(u'No Security Account Manager key found.')

  output_writer_object.Close()

  return True


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)
