# -*- coding: utf-8 -*-
"""Security Account Manager (SAM) collector."""

from __future__ import print_function
import datetime

import construct

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import semantic_time as dfdatetime_semantic_time

from winregrc import interface


class UserAccount(object):
  """Class that defines an user account.

  Attributes:
    account_expiration_time (dfdatetime.DateTimeValues): account expiration
      date and time.
    codepage (str): code page.
    comment (str): comment.
    full_name (str): full name.
    last_login_time (dfdatetime.DateTimeValues): last log-in date and time.
    last_password_failure_time (dfdatetime.DateTimeValues): last password
        failure date and time.
    last_password_set_time (dfdatetime.DateTimeValues): last password set
        date and time.
    name (str): name
    number_of_logons (int): number of log-ons.
    number_of_password_failures (int): number of password failures.
    primary_gid (int): primary group identifier (GID).
    rid (str): relative identifier (RID).
    user_account_control_flags (int): user account control flags.
    user_comment (str): user comment.
    username (str): username.
  """

  def __init__(self):
    """Initializes an user account."""
    super(UserAccount, self).__init__()
    self.account_expiration_time = None
    self.codepage = None
    self.comment = None
    self.full_name = None
    self.last_login_time = None
    self.last_password_failure_time = None
    self.last_password_set_time = None
    self.name = None
    self.number_of_logons = None
    self.number_of_password_failures = None
    self.primary_gid = None
    self.rid = None
    self.user_account_control_flags = None
    self.user_comment = None
    self.username = None


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

  def _CopyFiletimeToString(self, filetime):
    """Retrieves a string representation of the FILETIME timestamp value.

    Args:
      filetime (int): a FILETIME timestamp value.

    Returns:
      str: string representation of the FILETIME timestamp value.
    """
    if filetime == 0:
      return u'Not set'

    if filetime == 0x7fffffffffffffff:
      return u'Never'

    filetime, _ = divmod(filetime, 10)
    date_time = (datetime.datetime(1601, 1, 1) +
                 datetime.timedelta(microseconds=filetime))

    return u'{0!s}'.format(date_time)

  def _ParseFiletime(self, filetime):
    """Parses a FILETIME timestamp value.

    Args:
      filetime (int): a FILETIME timestamp value.

    Returns:
      dfdatetime.DateTimeValues: date and time values.
    """
    if filetime == 0:
      return dfdatetime_semantic_time.SemanticTime(string=u'Not set')

    if filetime == 0x7fffffffffffffff:
      return dfdatetime_semantic_time.SemanticTime(string=u'Never')

    return dfdatetime_filetime.Filetime(timestamp=filetime)

  def ParseFValue(self, value_data, user_account):
    """Parses the F value data.

    Args:
      value_data (bytes): F value data.
      user_account (UserAccount): user account.
    """
    f_value_struct = self._F_VALUE_STRUCT.parse(value_data)

    if self._debug:
      self._output_writer.WriteDebugData(u'F value data:', value_data)

    # TODO: change FILETIME timestamps into date time values.
    # date_time = self._ParseFiletime(f_value_struct.last_login_time)

    user_account.last_login_time = f_value_struct.last_login_time

    user_account.last_password_set_time = f_value_struct.last_password_set_time
    user_account.account_expiration_time = (
        f_value_struct.account_expiration_time)
    user_account.last_password_failure_time = (
        f_value_struct.last_password_failure_time)
    user_account.rid = f_value_struct.rid
    user_account.primary_gid = f_value_struct.primary_gid
    user_account.user_account_control_flags = (
        f_value_struct.user_account_control_flags)
    user_account.codepage = f_value_struct.codepage
    user_account.number_of_password_failures = (
        f_value_struct.number_of_password_failures)
    user_account.number_of_logons = f_value_struct.number_of_logons

    if self._debug:
      value_string = u'{0:d}'.format(f_value_struct.major_version)
      self._output_writer.WriteValue(u'Major version', value_string)

      value_string = u'{0:d}'.format(f_value_struct.minor_version)
      self._output_writer.WriteValue(u'Minor version', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown1)
      self._output_writer.WriteValue(u'Unknown1', value_string)

      date_string = self._CopyFiletimeToString(f_value_struct.last_login_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_login_time)
      self._output_writer.WriteValue(u'Last login time', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown2)
      self._output_writer.WriteValue(u'Unknown2', value_string)

      date_string = self._CopyFiletimeToString(
          f_value_struct.last_password_set_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_password_set_time)
      self._output_writer.WriteValue(
          u'Last password set time', value_string)

      date_string = self._CopyFiletimeToString(
          f_value_struct.account_expiration_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value_struct.account_expiration_time)
      self._output_writer.WriteValue(
          u'Account expiration time', value_string)

      date_string = self._CopyFiletimeToString(
          f_value_struct.last_password_failure_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value_struct.last_password_failure_time)
      self._output_writer.WriteValue(
          u'Last password failure time', value_string)

      value_string = u'{0:d}'.format(f_value_struct.rid)
      self._output_writer.WriteValue(
          u'Relative identifier (RID)', value_string)

      value_string = u'{0:d}'.format(f_value_struct.primary_gid)
      self._output_writer.WriteValue(
          u'Primary group identifier (GID)', value_string)

      value_string = u'0x{0:08x}'.format(
          f_value_struct.user_account_control_flags)
      self._output_writer.WriteValue(
          u'User account control flags', value_string)

      if f_value_struct.user_account_control_flags:
        for flag, identifier in sorted(
            self._USER_ACCOUNT_CONTROL_FLAGS.items()):
          if flag & f_value_struct.user_account_control_flags:
            value_string = u'\t{0:s} (0x{1:08x})'.format(identifier, flag)
            self._output_writer.WriteText(value_string)

        self._output_writer.WriteText(u'')

      value_string = u'0x{0:04x}'.format(f_value_struct.country_code)
      self._output_writer.WriteValue(u'Country code', value_string)

      value_string = u'{0:d}'.format(f_value_struct.codepage)
      self._output_writer.WriteValue(u'Codepage', value_string)

      value_string = u'{0:d}'.format(f_value_struct.number_of_password_failures)
      self._output_writer.WriteValue(
          u'Number of password failures', value_string)

      value_string = u'{0:d}'.format(f_value_struct.number_of_logons)
      self._output_writer.WriteValue(u'Number of logons', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown6)
      self._output_writer.WriteValue(u'Unknown6', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown7)
      self._output_writer.WriteValue(u'Unknown7', value_string)

      value_string = u'0x{0:08x}'.format(f_value_struct.unknown8)
      self._output_writer.WriteValue(u'Unknown8', value_string)

      self._output_writer.WriteText(u'')

  def ParseVValue(self, value_data, user_account):
    """Parses the V value data.

    Args:
      value_data (bytes): V value data.
      user_account (UserAccount): user account.
    """
    v_value_struct = self._V_VALUE_STRUCT.parse(value_data)

    if self._debug:
      self._output_writer.WriteDebugData(u'V value data:', value_data)

    for index in range(0, 17):
      user_information_descriptor = (
          v_value_struct.user_information_descriptor[index])

      data_start_offset = user_information_descriptor.offset + 0xcc
      data_end_offset = data_start_offset + user_information_descriptor.size
      descriptor_data = value_data[data_start_offset:data_end_offset]

      if self._debug:
        description_string = u'Descriptor: {0:d} description'.format(index + 1)
        value_string = self._USER_INFORMATION_DESCRIPTORS[index]
        self._output_writer.WriteValue(description_string, value_string)

        offset_string = u'Descriptor: {0:d} offset'.format(index + 1)
        value_string = u'0x{0:08x} (0x{1:08x})'.format(
            user_information_descriptor.offset, data_start_offset)
        self._output_writer.WriteValue(offset_string, value_string)

        size_string = u'Descriptor: {0:d} size'.format(index + 1)
        value_string = u'{0:d}'.format(user_information_descriptor.size)
        self._output_writer.WriteValue(size_string, value_string)

        unknown1_string = u'Descriptor: {0:d} unknown1'.format(index + 1)
        value_string = u'0x{0:08x}'.format(user_information_descriptor.unknown1)
        self._output_writer.WriteValue(unknown1_string, value_string)

        data_string = u'Descriptor: {0:d} data:'.format(index + 1)
        self._output_writer.WriteDebugData(data_string, descriptor_data)

      if index == 1:
        user_account.username = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(
              u'Username', user_account.username)
          self._output_writer.WriteText(u'')

      elif index == 2:
        user_account.full_name = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(
              u'Full name', user_account.full_name)
          self._output_writer.WriteText(u'')

      elif index == 3:
        user_account.comment = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(u'Comment', user_account.comment)
          self._output_writer.WriteText(u'')

      elif index == 4:
        user_account.user_comment = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(
              u'User comment', user_account.user_comment)
          self._output_writer.WriteText(u'')

    if self._debug:
      self._output_writer.WriteText(u'')


class SecurityAccountManagerCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a Security Account Manager (SAM) collector."""

  def Collect(self, registry, output_writer):
    """Collects the Security Account Manager (SAM) information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Security Account Manager (SAM) information key was
          found, False if not.
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

      user_account = UserAccount()

      f_value = subkey.GetValueByName(u'F')
      if f_value:
        parser.ParseFValue(f_value.data, user_account)

      v_value = subkey.GetValueByName(u'V')
      if v_value:
        parser.ParseVValue(v_value.data, user_account)

      output_writer.WriteUserAccount(user_account)

    return True
