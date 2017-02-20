# -*- coding: utf-8 -*-
"""Security Account Manager (SAM) collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfdatetime import filetime as dfdatetime_filetime

from winregrc import hexdump
from winregrc import interface


# pylint: disable=logging-format-interpolation

class SecurityAccountManagerDataParser(object):
  """Class that parses the Security Account Manager (SAM) data."""

  _F_VALUE_STRUCT = construct.Struct(
      u'f_value_struct',
      construct.ULInt16(u'major_version'),
      construct.ULInt16(u'minor_version'),
      construct.ULInt32(u'unknown1'),
      construct.ULInt64(u'last_login_time'),
      construct.ULInt64(u'unknown2'),
      construct.ULInt64(u'last_password_set_time'),
      construct.ULInt64(u'account_expiration_time'),
      construct.ULInt64(u'last_password_failure_time'),
      construct.ULInt32(u'rid'),
      construct.ULInt32(u'primary_gid'),
      construct.ULInt32(u'user_account_control_flags'),
      construct.ULInt16(u'country_code'),
      construct.ULInt16(u'codepage'),
      construct.ULInt16(u'number_of_password_failures'),
      construct.ULInt16(u'number_of_logons'),
      construct.ULInt32(u'unknown6'),
      construct.ULInt32(u'unknown7'),
      construct.ULInt32(u'unknown8'))

  _USER_INFORMATION_DESCRIPTOR = construct.Struct(
      u'user_information_descriptor',
      construct.ULInt32(u'offset'),
      construct.ULInt32(u'size'),
      construct.ULInt32(u'unknown1'))

  _V_VALUE_STRUCT = construct.Struct(
      u'v_value_struct',
      construct.Array(17, _USER_INFORMATION_DESCRIPTOR))

  _USER_INFORMATION_DESCRIPTORS = [
      u'security descriptor',
      u'username',
      u'full name',
      u'comment',
      u'user comment',
      u'unknown1',
      u'home directory',
      u'home directory connect',
      u'script path',
      u'profile path',
      u'workstations',
      u'hours allowed',
      u'unknown2',
      u'LM hash',
      u'NTLM hash',
      u'unknown3',
      u'unknown4']

  _USER_ACCOUNT_CONTROL_FLAGS = {
      0x00000001: u'USER_ACCOUNT_DISABLED',
      0x00000002: u'USER_HOME_DIRECTORY_REQUIRED',
      0x00000004: u'USER_PASSWORD_NOT_REQUIRED',
      0x00000008: u'USER_TEMP_DUPLICATE_ACCOUNT',
      0x00000010: u'USER_NORMAL_ACCOUNT',
      0x00000020: u'USER_MNS_LOGON_ACCOUNT',
      0x00000040: u'USER_INTERDOMAIN_TRUST_ACCOUNT',
      0x00000080: u'USER_WORKSTATION_TRUST_ACCOUNT',
      0x00000100: u'USER_SERVER_TRUST_ACCOUNT',
      0x00000200: u'USER_DONT_EXPIRE_PASSWORD',
      0x00000400: u'USER_ACCOUNT_AUTO_LOCKED',
      0x00000800: u'USER_ENCRYPTED_TEXT_PASSWORD_ALLOWED',
      0x00001000: u'USER_SMARTCARD_REQUIRED',
      0x00002000: u'USER_TRUSTED_FOR_DELEGATION',
      0x00004000: u'USER_NOT_DELEGATED',
      0x00008000: u'USER_USE_DES_KEY_ONLY',
      0x00010000: u'USER_DONT_REQUIRE_PREAUTH',
      0x00020000: u'USER_PASSWORD_EXPIRED',
      0x00040000: u'USER_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION',
      0x00080000: u'USER_NO_AUTH_DATA_REQUIRED',
      0x00100000: u'USER_PARTIAL_SECRETS_ACCOUNT',
      0x00200000: u'USER_USE_AES_KEYS'}

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Security Account Manager (SAM) data parser.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SecurityAccountManagerDataParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

  def ParseFValue(self, value_data):
    """Parses the F value data.

    Args:
      value_data (bytes): F value data.
    """
    f_value_struct = self._F_VALUE_STRUCT.parse(value_data)

    if self._debug:
      self._output_writer.WriteDebugData(u'F value data:', value_data)

    if self._debug:
      value_string = u'{0:d}'.format(f_value_struct.major_version)
      self._output_writer.WriteDebugValue(u'Major version', value_string)

      value_string = u'{0:d}'.format(f_value_struct.minor_version)
      self._output_writer.WriteDebugValue(u'Minor version', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown1)
      self._output_writer.WriteDebugValue(u'Unknown1', value_string)

      # date_time = dfdatetime_filetime.Filetime(timestamp=f_value_struct.last_login_time)

      if f_value_struct.last_login_time == 0:
        date_string = u'Not set'
      else:
        timestamp = f_value_struct.last_login_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

      value_string = u'{0!s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_login_time)
      self._output_writer.WriteDebugValue(u'Last login time', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown2)
      self._output_writer.WriteDebugValue(u'Unknown2', value_string)

      if f_value_struct.last_password_set_time == 0:
        date_string = u'Not set'
      else:
        timestamp = f_value_struct.last_password_set_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

      value_string = u'{0!s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_password_set_time)
      self._output_writer.WriteDebugValue(
          u'Last password set time', value_string)

      if f_value_struct.account_expiration_time == 0:
        date_string = u'Not set'
      elif f_value_struct.account_expiration_time == 0x7fffffffffffffff:
        date_string = u'Never'
      else:
        timestamp = f_value_struct.account_expiration_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

      value_string = u'{0!s} (0x{1:08x})'.format(
          date_string, f_value_struct.account_expiration_time)
      self._output_writer.WriteDebugValue(
          u'Account expiration time', value_string)

      if f_value_struct.last_password_failure_time == 0:
        date_string = u'Not set'
      else:
        timestamp = f_value_struct.last_password_failure_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

      value_string = u'{0!s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_password_failure_time)
      self._output_writer.WriteDebugValue(
          u'Last password failure time', value_string)

      value_string = u'{0:d}'.format(f_value_struct.rid)
      self._output_writer.WriteDebugValue(
          u'Relative identifier (RID)', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.primary_gid)
      self._output_writer.WriteDebugValue(
          u'Primary group identifier (GID)', value_string)

      value_string = u'0x{0:08x}'.format(
          f_value_struct.user_account_control_flags)
      self._output_writer.WriteDebugValue(
          u'User account control flags', value_string)

      if f_value_struct.user_account_control_flags:
        for flag, identifier in sorted(
            self._USER_ACCOUNT_CONTROL_FLAGS.items()):
          if flag & f_value_struct.user_account_control_flags:
            value_string = u'\t{0:s} (0x{1:08x})'.format(identifier, flag)
            self._output_writer.WriteDebugText(value_string)

        self._output_writer.WriteDebugText(u'')

      value_string = u'0x{0:04x}'.format(f_value_struct.country_code)
      self._output_writer.WriteDebugValue(u'Country code', value_string)

      value_string = u'{0:d}'.format(f_value_struct.codepage)
      self._output_writer.WriteDebugValue(u'Codepage', value_string)

      value_string = u'{0:d}'.format(f_value_struct.number_of_password_failures)
      self._output_writer.WriteDebugValue(
          u'Number of password failures', value_string)

      value_string = u'{0:d}'.format(f_value_struct.number_of_logons)
      self._output_writer.WriteDebugValue(u'Number of logons', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown6)
      self._output_writer.WriteDebugValue(u'Unknown6', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown7)
      self._output_writer.WriteDebugValue(u'Unknown7', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown8)
      self._output_writer.WriteDebugValue(u'Unknown8', value_string)

      self._output_writer.WriteDebugText(u'')

  def ParseVValue(self, value_data):
    """Parses the V value data.

    Args:
      value_data (bytes): V value data.
    """
    v_value_struct = self._V_VALUE_STRUCT.parse(value_data)

    if self._debug:
      self._output_writer.WriteDebugData(u'V value data:', value_data)

    if self._debug:
      for index in range(0, 17):
        user_information_descriptor = (
            v_value_struct.user_information_descriptor[index])

        data_start_offset = user_information_descriptor.offset + 0xcc
        data_end_offset = data_start_offset + user_information_descriptor.size

        description_string = u'Descriptor: {0:d} description'.format(index + 1)
        value_string = self._USER_INFORMATION_DESCRIPTORS[index]
        self._output_writer.WriteDebugValue(description_string, value_string)

        offset_string = u'Descriptor: {0:d} offset'.format(index + 1)
        value_string = u'0x{0:08x} (0x{1:08x})'.format(
            user_information_descriptor.offset, data_start_offset)
        self._output_writer.WriteDebugValue(offset_string, value_string)

        size_string = u'Descriptor: {0:d} size'.format(index + 1)
        value_string = u'{0:d}'.format(user_information_descriptor.size)
        self._output_writer.WriteDebugValue(size_string, value_string)

        unknown1_string = u'Descriptor: {0:d} unknown1'.format(index + 1)
        value_string = u'0x{0:08x}'.format(user_information_descriptor.unknown1)
        self._output_writer.WriteDebugValue(unknown1_string, value_string)

        data_string = u'Descriptor: {0:d} data:'.format(index + 1)
        self._output_writer.WriteDebugData(
            data_string, value_data[data_start_offset:data_end_offset])

      self._output_writer.WriteDebugText(u'')


class SecurityAccountManagerCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a Security Account Manager (SAM) collector."""

  def Collect(self, registry, output_writer):
    """Collects the Security Account Manager (SAM) information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Security Account Manager (SAM) information key was found,
          False if not.
    """
    key_path = u'HKEY_LOCAL_MACHINE\\SAM\\SAM\\Domains\\Account\\Users'
    users_key = registry.GetKeyByPath(key_path)
    if not users_key:
      return False

    parser = SecurityAccountManagerDataParser(
        debug=self._debug, output_writer=output_writer)

    for subkey in users_key.GetSubkeys():
      if subkey.name == u'Names':
        continue

      f_value = subkey.GetValueByName(u'F')
      if f_value:
        parser.ParseFValue(f_value.data)

      v_value = subkey.GetValueByName(u'V')
      if v_value:
        parser.ParseVValue(v_value.data)

    return True
