# -*- coding: utf-8 -*-
"""Security Accounts Manager (SAM) collector."""

from __future__ import unicode_literals

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import semantic_time as dfdatetime_semantic_time

from winregrc import data_format
from winregrc import errors
from winregrc import interface


class UserAccount(object):
  """User account.

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


class SecurityAccountManagerDataParser(data_format.BinaryDataFormat):
  """Security Accounts Manager (SAM) data parser."""

  _DEFINITION_FILE = 'sam.yaml'

  _USER_INFORMATION_DESCRIPTORS = [
      'security descriptor',
      'username',
      'full name',
      'comment',
      'user comment',
      'unknown1',
      'home directory',
      'home directory connect',
      'script path',
      'profile path',
      'workstations',
      'hours allowed',
      'unknown2',
      'LM hash',
      'NTLM hash',
      'unknown3',
      'unknown4']

  _USER_ACCOUNT_CONTROL_FLAGS = {
      0x00000001: 'USER_ACCOUNT_DISABLED',
      0x00000002: 'USER_HOME_DIRECTORY_REQUIRED',
      0x00000004: 'USER_PASSWORD_NOT_REQUIRED',
      0x00000008: 'USER_TEMP_DUPLICATE_ACCOUNT',
      0x00000010: 'USER_NORMAL_ACCOUNT',
      0x00000020: 'USER_MNS_LOGON_ACCOUNT',
      0x00000040: 'USER_INTERDOMAIN_TRUST_ACCOUNT',
      0x00000080: 'USER_WORKSTATION_TRUST_ACCOUNT',
      0x00000100: 'USER_SERVER_TRUST_ACCOUNT',
      0x00000200: 'USER_DONT_EXPIRE_PASSWORD',
      0x00000400: 'USER_ACCOUNT_AUTO_LOCKED',
      0x00000800: 'USER_ENCRYPTED_TEXT_PASSWORD_ALLOWED',
      0x00001000: 'USER_SMARTCARD_REQUIRED',
      0x00002000: 'USER_TRUSTED_FOR_DELEGATION',
      0x00004000: 'USER_NOT_DELEGATED',
      0x00008000: 'USER_USE_DES_KEY_ONLY',
      0x00010000: 'USER_DONT_REQUIRE_PREAUTH',
      0x00020000: 'USER_PASSWORD_EXPIRED',
      0x00040000: 'USER_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION',
      0x00080000: 'USER_NO_AUTH_DATA_REQUIRED',
      0x00100000: 'USER_PARTIAL_SECRETS_ACCOUNT',
      0x00200000: 'USER_USE_AES_KEYS'}

  def _DebugPrintFValue(self, f_value):
    """Prints F value debug information.

    Args:
      f_value (f_value): F value.
    """
    self._DebugPrintDecimalValue('Major version', f_value.major_version)

    self._DebugPrintDecimalValue('Minor version', f_value.minor_version)

    value_string = '0x{0:08x}'.format(f_value.unknown1)
    self._DebugPrintValue('Unknown1', value_string)

    self._DebugPrintFiletimeValue('Last login time', f_value.last_login_time)

    value_string = '0x{0:08x}'.format(f_value.unknown2)
    self._DebugPrintValue('Unknown2', value_string)

    self._DebugPrintFiletimeValue(
        'Last password set time', f_value.last_password_set_time)

    self._DebugPrintFiletimeValue(
        'Account expiration time', f_value.account_expiration_time)

    self._DebugPrintFiletimeValue(
        'Last password failure time', f_value.last_password_failure_time)

    self._DebugPrintDecimalValue('Relative identifier (RID)', f_value.rid)

    self._DebugPrintDecimalValue(
        'Primary group identifier (GID)', f_value.primary_gid)

    value_string = '0x{0:08x}'.format(f_value.user_account_control_flags)
    self._DebugPrintValue('User account control flags', value_string)

    if f_value.user_account_control_flags:
      for flag, identifier in sorted(
          self._USER_ACCOUNT_CONTROL_FLAGS.items()):
        if flag & f_value.user_account_control_flags:
          value_string = '\t{0:s} (0x{1:08x})'.format(identifier, flag)
          self._DebugPrintText(value_string)

      self._DebugPrintText('')

    value_string = '0x{0:04x}'.format(f_value.country_code)
    self._DebugPrintValue('Country code', value_string)

    self._DebugPrintDecimalValue('Codepage', f_value.codepage)

    self._DebugPrintDecimalValue(
        'Number of password failures', f_value.number_of_password_failures)

    self._DebugPrintDecimalValue('Number of logons', f_value.number_of_logons)

    value_string = '0x{0:08x}'.format(f_value.unknown6)
    self._DebugPrintValue('Unknown6', value_string)

    value_string = '0x{0:08x}'.format(f_value.unknown7)
    self._DebugPrintValue('Unknown7', value_string)

    value_string = '0x{0:08x}'.format(f_value.unknown8)
    self._DebugPrintValue('Unknown8', value_string)

    self._DebugPrintText('')

  def _ParseFiletime(self, filetime):
    """Parses a FILETIME timestamp value.

    Args:
      filetime (int): a FILETIME timestamp value.

    Returns:
      dfdatetime.DateTimeValues: date and time values.
    """
    if filetime == 0:
      return dfdatetime_semantic_time.SemanticTime(string='Not set')

    if filetime == 0x7fffffffffffffff:
      return dfdatetime_semantic_time.SemanticTime(string='Never')

    return dfdatetime_filetime.Filetime(timestamp=filetime)

  def ParseFValue(self, value_data, user_account):
    """Parses the F value data.

    Args:
      value_data (bytes): F value data.
      user_account (UserAccount): user account.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('f_value')

    try:
      f_value = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'F value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse F value with error: {0!s}'.format(exception))

    # TODO: change FILETIME timestamps into date time values.
    # date_time = self._ParseFiletime(f_value.last_login_time)

    user_account.last_login_time = f_value.last_login_time

    user_account.last_password_set_time = f_value.last_password_set_time
    user_account.account_expiration_time = f_value.account_expiration_time
    user_account.last_password_failure_time = f_value.last_password_failure_time
    user_account.rid = f_value.rid
    user_account.primary_gid = f_value.primary_gid
    user_account.user_account_control_flags = f_value.user_account_control_flags
    user_account.codepage = f_value.codepage
    user_account.number_of_password_failures = (
        f_value.number_of_password_failures)
    user_account.number_of_logons = f_value.number_of_logons

    if self._debug:
      self._DebugPrintFValue(f_value)

  def ParseVValue(self, value_data, user_account):
    """Parses the V value data.

    Args:
      value_data (bytes): V value data.
      user_account (UserAccount): user account.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('v_value')

    try:
      v_value = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'V value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse F value with error: {0!s}'.format(exception))

    for index in range(0, 17):
      user_information_descriptor = v_value[index]

      data_start_offset = user_information_descriptor.offset + 0xcc
      data_end_offset = data_start_offset + user_information_descriptor.size
      descriptor_data = value_data[data_start_offset:data_end_offset]

      if self._debug:
        description_string = 'Descriptor: {0:d} description'.format(index + 1)
        value_string = self._USER_INFORMATION_DESCRIPTORS[index]
        self._DebugPrintValue(description_string, value_string)

        value_description = 'Descriptor: {0:d} offset'.format(index + 1)
        value_string = '0x{0:08x} (0x{1:08x})'.format(
            user_information_descriptor.offset, data_start_offset)
        self._DebugPrintValue(value_description, value_string)

        value_description = 'Descriptor: {0:d} size'.format(index + 1)
        self._DebugPrintDecimalValue(
            value_description, user_information_descriptor.size)

        unknown1_string = 'Descriptor: {0:d} unknown1'.format(index + 1)
        value_string = '0x{0:08x}'.format(user_information_descriptor.unknown1)
        self._DebugPrintValue(unknown1_string, value_string)

        data_string = 'Descriptor: {0:d} data:'.format(index + 1)
        self._DebugPrintData(data_string, descriptor_data)

      if index == 1:
        user_account.username = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Username', user_account.username)
          self._DebugPrintText('')

      elif index == 2:
        user_account.full_name = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Full name', user_account.full_name)
          self._DebugPrintText('')

      elif index == 3:
        user_account.comment = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Comment', user_account.comment)
          self._DebugPrintText('')

      elif index == 4:
        user_account.user_comment = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue(
              'User comment', user_account.user_comment)
          self._DebugPrintText('')

    if self._debug:
      self._DebugPrintText('')


class SecurityAccountManagerCollector(interface.WindowsRegistryKeyCollector):
  """Security Accounts Manager (SAM) collector.

  Attributes:
    user_accounts (list[UserAccount]): user accounts.
  """

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Security Accounts Manager (SAM) collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SecurityAccountManagerCollector, self).__init__(debug=debug)
    self._output_writer = output_writer
    self.user_accounts = []

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects the Security Accounts Manager (SAM) information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the Security Accounts Manager (SAM) information key was
          found, False if not.
    """
    key_path = 'HKEY_LOCAL_MACHINE\\SAM\\SAM\\Domains\\Account\\Users'
    users_key = registry.GetKeyByPath(key_path)
    if not users_key:
      return False

    parser = SecurityAccountManagerDataParser(
        debug=self._debug, output_writer=self._output_writer)

    for subkey in users_key.GetSubkeys():
      if subkey.name == 'Names':
        continue

      user_account = UserAccount()

      f_value = subkey.GetValueByName('F')
      if f_value:
        parser.ParseFValue(f_value.data, user_account)

      v_value = subkey.GetValueByName('V')
      if v_value:
        parser.ParseVValue(v_value.data, user_account)

      self.user_accounts.append(user_account)

    return True
