# -*- coding: utf-8 -*-
"""Security Account Manager (SAM) collector."""

import datetime

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import semantic_time as dfdatetime_semantic_time

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

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


class SecurityAccountManagerDataParser(object):
  """Security Account Manager (SAM) data parser."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
      b'name: uint16',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 2',
      b'  units: bytes',
      b'---',
      b'name: uint32',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 4',
      b'  units: bytes',
      b'---',
      b'name: uint64',
      b'type: integer',
      b'attributes:',
      b'  format: unsigned',
      b'  size: 8',
      b'  units: bytes',
      b'---',
      b'name: f_value',
      b'type: structure',
      b'description: Security Account Manager F value.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: major_version',
      b'  data_type: uint16',
      b'- name: minor_version',
      b'  data_type: uint16',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: last_login_time',
      b'  data_type: uint64',
      b'- name: unknown2',
      b'  data_type: uint64',
      b'- name: last_password_set_time',
      b'  data_type: uint64',
      b'- name: account_expiration_time',
      b'  data_type: uint64',
      b'- name: last_password_failure_time',
      b'  data_type: uint64',
      b'- name: rid',
      b'  data_type: uint32',
      b'- name: primary_gid',
      b'  data_type: uint32',
      b'- name: user_account_control_flags',
      b'  data_type: uint32',
      b'- name: country_code',
      b'  data_type: uint16',
      b'- name: codepage',
      b'  data_type: uint16',
      b'- name: number_of_password_failures',
      b'  data_type: uint16',
      b'- name: number_of_logons',
      b'  data_type: uint16',
      b'- name: unknown6',
      b'  data_type: uint32',
      b'- name: unknown7',
      b'  data_type: uint32',
      b'- name: unknown8',
      b'  data_type: uint32',
      b'---',
      b'name: user_information_descriptor',
      b'type: structure',
      b'description: Security Account Manager user information descriptor.',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: offset',
      b'  data_type: uint32',
      b'- name: size',
      b'  data_type: uint32',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'---',
      b'name: v_value',
      b'type: sequence',
      b'description: Security Account Manager V value.',
      b'element_data_type: user_information_descriptor',
      b'number_of_elements: 17'])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _F_VALUE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'f_value')

  _V_VALUE = _DATA_TYPE_FABRIC.CreateDataTypeMap(u'v_value')

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

    Raises:
      ParseError: if the value data could not be parsed.
    """
    try:
      f_value = self._F_VALUE.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    if self._debug:
      self._output_writer.WriteDebugData(u'F value data:', value_data)

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
      self._output_writer.WriteIntegerValueAsDecimal(
          u'Major version', f_value.major_version)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Minor version', f_value.minor_version)

      value_string = u'0x{0:08x}'.format(f_value.unknown1)
      self._output_writer.WriteValue(u'Unknown1', value_string)

      date_string = self._CopyFiletimeToString(f_value.last_login_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value.last_login_time)
      self._output_writer.WriteValue(u'Last login time', value_string)

      value_string = u'0x{0:08x}'.format(f_value.unknown2)
      self._output_writer.WriteValue(u'Unknown2', value_string)

      date_string = self._CopyFiletimeToString(f_value.last_password_set_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value.last_password_set_time)
      self._output_writer.WriteValue(u'Last password set time', value_string)

      date_string = self._CopyFiletimeToString(f_value.account_expiration_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value.account_expiration_time)
      self._output_writer.WriteValue(u'Account expiration time', value_string)

      date_string = self._CopyFiletimeToString(
          f_value.last_password_failure_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, f_value.last_password_failure_time)
      self._output_writer.WriteValue(
          u'Last password failure time', value_string)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Relative identifier (RID)', f_value.rid)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Primary group identifier (GID)', f_value.primary_gid)

      value_string = u'0x{0:08x}'.format(f_value.user_account_control_flags)
      self._output_writer.WriteValue(
          u'User account control flags', value_string)

      if f_value.user_account_control_flags:
        for flag, identifier in sorted(
            self._USER_ACCOUNT_CONTROL_FLAGS.items()):
          if flag & f_value.user_account_control_flags:
            value_string = u'\t{0:s} (0x{1:08x})'.format(identifier, flag)
            self._output_writer.WriteText(value_string)

        self._output_writer.WriteText(u'')

      value_string = u'0x{0:04x}'.format(f_value.country_code)
      self._output_writer.WriteValue(u'Country code', value_string)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Codepage', f_value.codepage)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Number of password failures', f_value.number_of_password_failures)

      self._output_writer.WriteIntegerValueAsDecimal(
          u'Number of logons', f_value.number_of_logons)

      value_string = u'0x{0:08x}'.format(f_value.unknown6)
      self._output_writer.WriteValue(u'Unknown6', value_string)

      value_string = u'0x{0:08x}'.format(f_value.unknown7)
      self._output_writer.WriteValue(u'Unknown7', value_string)

      value_string = u'0x{0:08x}'.format(f_value.unknown8)
      self._output_writer.WriteValue(u'Unknown8', value_string)

      self._output_writer.WriteText(u'')

  def ParseVValue(self, value_data, user_account):
    """Parses the V value data.

    Args:
      value_data (bytes): V value data.
      user_account (UserAccount): user account.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    try:
      v_value = self._V_VALUE.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    if self._debug:
      self._output_writer.WriteDebugData(u'V value data:', value_data)

    for index in range(0, 17):
      user_information_descriptor = v_value[index]

      data_start_offset = user_information_descriptor.offset + 0xcc
      data_end_offset = data_start_offset + user_information_descriptor.size
      descriptor_data = value_data[data_start_offset:data_end_offset]

      if self._debug:
        description_string = u'Descriptor: {0:d} description'.format(index + 1)
        value_string = self._USER_INFORMATION_DESCRIPTORS[index]
        self._output_writer.WriteValue(description_string, value_string)

        value_description = u'Descriptor: {0:d} offset'.format(index + 1)
        value_string = u'0x{0:08x} (0x{1:08x})'.format(
            user_information_descriptor.offset, data_start_offset)
        self._output_writer.WriteValue(value_description, value_string)

        value_description = u'Descriptor: {0:d} size'.format(index + 1)
        self._output_writer.WriteIntegerValueAsDecimal(
            value_description, user_information_descriptor.size)

        unknown1_string = u'Descriptor: {0:d} unknown1'.format(index + 1)
        value_string = u'0x{0:08x}'.format(user_information_descriptor.unknown1)
        self._output_writer.WriteValue(unknown1_string, value_string)

        data_string = u'Descriptor: {0:d} data:'.format(index + 1)
        self._output_writer.WriteDebugData(data_string, descriptor_data)

      if index == 1:
        user_account.username = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(u'Username', user_account.username)
          self._output_writer.WriteText(u'')

      elif index == 2:
        user_account.full_name = descriptor_data.decode(
            u'utf-16-le').rstrip(u'\x00')

        if self._debug:
          self._output_writer.WriteValue(u'Full name', user_account.full_name)
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
  """Security Account Manager (SAM) collector."""

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
