# -*- coding: utf-8 -*-
"""Security Accounts Manager (SAM) collector."""

import pyfwnt

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

  _DEBUG_INFO_C_VALUE = [
      ('format_version', 'Format version', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('unknown2', 'Unknown1', '_FormatIntegerAsHexadecimal4'),
      ('security_descriptor_size', 'Security descriptor size',
       '_FormatIntegerAsDecimal'),
      ('unknown3', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('unknown4', 'Unknown1', '_FormatIntegerAsHexadecimal2'),
      ('security_descriptor', 'Security descriptor',
       '_FormatSecurityDescriptor')]

  _DEBUG_INFO_F_VALUE = [
      ('major_version', 'Major version', '_FormatIntegerAsDecimal'),
      ('minor_version', 'Minor version', '_FormatIntegerAsDecimal'),
      ('unknown1', 'Unknown1', '_FormatIntegerAsHexadecimal8'),
      ('last_login_time', 'Last login time', '_FormatIntegerAsFiletime'),
      ('unknown2', 'Unknown2', '_FormatIntegerAsHexadecimal8'),
      ('last_password_set_time', 'Last password set time',
       '_FormatIntegerAsFiletime'),
      ('account_expiration_time', 'Account expiration time',
       '_FormatIntegerAsFiletime'),
      ('last_password_failure_time', 'Last password failure time',
       '_FormatIntegerAsFiletime'),
      ('rid', 'Relative identifier (RID)', '_FormatIntegerAsDecimal'),
      ('primary_gid', 'Primary group identifier (GID)',
       '_FormatIntegerAsDecimal'),
      ('user_account_control_flags', 'User account control flags',
       '_FormatIntegerAsHexadecimal8'),
      ('user_account_control_flags', None, '_FormatUserAccountControlFlags'),
      ('country_code', 'Country code', '_FormatIntegerAsHexadecimal4'),
      ('codepage', 'Codepage', '_FormatIntegerAsDecimal'),
      ('number_of_password_failures', 'Number of password failures',
       '_FormatIntegerAsDecimal'),
      ('number_of_logons', 'Number of logons', '_FormatIntegerAsDecimal'),
      ('unknown6', 'Unknown6', '_FormatIntegerAsHexadecimal8'),
      ('unknown7', 'Unknown7', '_FormatIntegerAsHexadecimal8'),
      ('unknown8', 'Unknown8', '_FormatIntegerAsHexadecimal8')]

  # pylint: disable=no-member,using-constant-test

  def _FormatSecurityDescriptor(self, security_descriptor_data):
    """Formats security descriptor.

    Args:
      security_descriptor_data (bytes): security descriptor data.

    Returns:
      str: formatted security descriptor.
    """
    fwnt_descriptor = pyfwnt.security_descriptor()
    fwnt_descriptor.copy_from_byte_stream(security_descriptor_data)

    lines = []

    if fwnt_descriptor.owner:
      identifier_string = fwnt_descriptor.owner.get_string()
      value_string = '\tOwner: {0:s}'.format(identifier_string)
      lines.append(value_string)

    if fwnt_descriptor.group:
      identifier_string = fwnt_descriptor.group.get_string()
      value_string = '\tGroup: {0:s}'.format(identifier_string)
      lines.append(value_string)

    # TODO: format SACL
    # TODO: format DACL

    lines.append('')
    return '\n'.join(lines)

  # pylint: enable=no-member,using-constant-test

  def _FormatUserAccountControlFlags(self, user_account_control_flags):
    """Formats user account control flags.

    Args:
      user_account_control_flags (int): user account control flags.

    Returns:
      str: formatted user account control flags.
    """
    lines = []
    if user_account_control_flags:
      for flag, identifier in sorted(
          self._USER_ACCOUNT_CONTROL_FLAGS.items()):
        if flag & user_account_control_flags:
          value_string = '\t{0:s} (0x{1:08x})'.format(identifier, flag)
          lines.append(value_string)

      lines.append('')

    lines.append('')
    return '\n'.join(lines)

  def ParseCValue(self, value_data):
    """Parses the C value data.

    Args:
      value_data (bytes): F value data.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('c_value')

    try:
      c_value = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'C value')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          'Unable to parse C value with error: {0!s}'.format(exception))

    if self._debug:
      self._DebugPrintStructureObject(c_value, self._DEBUG_INFO_C_VALUE)

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
      self._DebugPrintStructureObject(f_value, self._DEBUG_INFO_F_VALUE)

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
          'Unable to parse V value with error: {0!s}'.format(exception))

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

        data_string = 'Descriptor: {0:d} data'.format(index + 1)
        self._DebugPrintData(data_string, descriptor_data)

      if index == 1:
        user_account.username = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Username', user_account.username)
          self._DebugPrintText('\n')

      elif index == 2:
        user_account.full_name = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Full name', user_account.full_name)
          self._DebugPrintText('\n')

      elif index == 3:
        user_account.comment = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue('Comment', user_account.comment)
          self._DebugPrintText('\n')

      elif index == 4:
        user_account.user_comment = descriptor_data.decode(
            'utf-16-le').rstrip('\x00')

        if self._debug:
          self._DebugPrintValue(
              'User comment', user_account.user_comment)
          self._DebugPrintText('\n')

    if self._debug:
      self._DebugPrintText('\n')


class SecurityAccountManagerCollector(interface.WindowsRegistryKeyCollector):
  """Security Accounts Manager (SAM) collector.

  Attributes:
    user_accounts (list[UserAccount]): user accounts.
  """

  _USERS_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\SAM\\SAM\\Domains\\Account\\Users')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Security Accounts Manager (SAM) collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(SecurityAccountManagerCollector, self).__init__(debug=debug)
    self._parser = SecurityAccountManagerDataParser(
        debug=debug, output_writer=output_writer)

    self.user_accounts = []

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects the Security Accounts Manager (SAM) information.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the Security Accounts Manager (SAM) information key was
          found, False if not.
    """
    main_key = registry.GetKeyByPath('HKEY_LOCAL_MACHINE\\SAM\\SAM')
    if not main_key:
      return False

    c_value = main_key.GetValueByName('C')
    if c_value:
      self._parser.ParseCValue(c_value.data)

    users_key = registry.GetKeyByPath(self._USERS_KEY_PATH)
    if not users_key:
      return False

    for subkey in users_key.GetSubkeys():
      if subkey.name == 'Names':
        continue

      user_account = UserAccount()

      f_value = subkey.GetValueByName('F')
      if f_value:
        self._parser.ParseFValue(f_value.data, user_account)

      v_value = subkey.GetValueByName('V')
      if v_value:
        self._parser.ParseVValue(v_value.data, user_account)

      self.user_accounts.append(user_account)

    return True
