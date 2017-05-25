# -*- coding: utf-8 -*-
"""Task Cache collector."""

import datetime
import logging

from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import semantic_time as dfdatetime_semantic_time

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from winregrc import errors
from winregrc import interface


class CachedTask(object):
  """Cached task.

  Attributes:
    identifier (str): identifier.
    last_registered_time (dfdatetime.DateTimeValues): last registered
        date and time.
    launch_time (dfdatetime.DateTimeValues): launch date and time.
    name (str): name.
  """

  def __init__(self):
    """Initializes a cached task."""
    super(CachedTask, self).__init__()
    self.identifier = None
    self.last_registered_time = None
    self.launch_time = None
    self.name = None


class TaskCacheDataParser(object):
  """Task Cache data parser."""

  _DATA_TYPE_FABRIC_DEFINITION = b'\n'.join([
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
      b'name: dynamic_info_record',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: last_registered_time',
      b'  data_type: uint64',
      b'- name: launch_time',
      b'  data_type: uint64',
      b'- name: unknown2',
      b'  data_type: uint32',
      b'- name: unknown3',
      b'  data_type: uint32',
      b'---',
      b'name: dynamic_info2_record',
      b'type: structure',
      b'attributes:',
      b'  byte_order: little-endian',
      b'members:',
      b'- name: unknown1',
      b'  data_type: uint32',
      b'- name: last_registered_time',
      b'  data_type: uint64',
      b'- name: launch_time',
      b'  data_type: uint64',
      b'- name: unknown2',
      b'  data_type: uint32',
      b'- name: unknown3',
      b'  data_type: uint32',
      b'- name: unknown_time',
      b'  data_type: uint64'])

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _DYNAMIC_INFO_RECORD = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'dynamic_info_record')

  _DYNAMIC_INFO_RECORD_SIZE = _DYNAMIC_INFO_RECORD.GetByteSize()

  _DYNAMIC_INFO2_RECORD = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      u'dynamic_info2_record')

  _DYNAMIC_INFO2_RECORD_SIZE = _DYNAMIC_INFO2_RECORD.GetByteSize()

  _DYNAMIC_INFO_RECORDS = {
      _DYNAMIC_INFO_RECORD_SIZE: _DYNAMIC_INFO_RECORD,
      _DYNAMIC_INFO2_RECORD_SIZE: _DYNAMIC_INFO2_RECORD}

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Task Cache data parser.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TaskCacheDataParser, self).__init__()
    self._debug = debug
    self._output_writer = output_writer

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

  def CopyFiletimeToString(self, filetime):
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

  def ParseDynamicInfo(self, value_data, cached_task):
    """Parses the DynamicInfo value data.

    Args:
      value_data (bytes): DynamicInfo value data.
      cached_task (CachedTask): cached task.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    if self._debug:
      self._output_writer.WriteDebugData(u'DynamicInfo value data:', value_data)

    value_data_size = len(value_data)

    dynamic_info_struct = self._DYNAMIC_INFO_RECORDS.get(value_data_size, None)
    if not dynamic_info_struct:
      raise errors.ParseError(
          u'Unsupported value data size: {0:d}.'.format(value_data_size))

    try:
      dynamic_info = dynamic_info_struct.MapByteStream(value_data)
    except (
        dtfabric_errors.ByteStreamTooSmallError,
        dtfabric_errors.MappingError) as exception:
      raise errors.ParseError(exception)

    cached_task.last_registered_time = self._ParseFiletime(
        dynamic_info.last_registered_time)
    cached_task.launch_time = self._ParseFiletime(
        dynamic_info.launch_time)

    if self._debug:
      value_string = u'0x{0:08x}'.format(dynamic_info.unknown1)
      self._output_writer.WriteValue(u'Unknown1', value_string)

      # Note this is likely either the last registered time or
      # the update time.
      date_string = self.CopyFiletimeToString(dynamic_info.last_registered_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, dynamic_info.last_registered_time)
      self._output_writer.WriteValue(u'Last registered time', value_string)

      # Note this is likely the launch time.
      date_string = self.CopyFiletimeToString(dynamic_info.launch_time)
      value_string = u'{0:s} (0x{1:08x})'.format(
          date_string, dynamic_info.launch_time)
      self._output_writer.WriteValue(u'Launch time', value_string)

      value_string = u'0x{0:08x}'.format(dynamic_info.unknown2)
      self._output_writer.WriteValue(u'Unknown2', value_string)

      value_string = u'0x{0:08x}'.format(dynamic_info.unknown3)
      self._output_writer.WriteValue(u'Unknown3', value_string)

      unknown_time = dynamic_info.unknown_time
      if unknown_time is not None:
        date_string = self.CopyFiletimeToString(unknown_time)
        value_string = u'{0:s} (0x{1:08x})'.format(
            date_string, dynamic_info.unknown_time)
        self._output_writer.WriteValue(u'Unknown time', value_string)

      self._output_writer.WriteText(u'')


class TaskCacheCollector(interface.WindowsRegistryKeyCollector):
  """Task Cache collector."""

  _TASK_CACHE_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      u'Schedule\\TaskCache')

  def _GetIdValue(self, registry_key):
    """Retrieves the Id value from Task Cache Tree key.

    Args:
      registry_key (dfwinreg.WinRegistryKey): Windows Registry key.

    Yields:
      tuple[dfwinreg.WinRegistryKey, dfwinreg.WinRegistryValue]: Windows
          Registry key and value.
    """
    id_value = registry_key.GetValueByName(u'Id')
    if id_value:
      yield registry_key, id_value

    for subkey in registry_key.GetSubkeys():
      for value_key, id_value in self._GetIdValue(subkey):
        yield value_key, id_value

  def Collect(self, registry, output_writer):
    """Collects the Task Cache.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the Task Cache key was found, False if not.
    """
    dynamic_info_size_error_reported = False

    task_cache_key = registry.GetKeyByPath(self._TASK_CACHE_KEY_PATH)
    if not task_cache_key:
      return False

    tasks_key = task_cache_key.GetSubkeyByName(u'Tasks')
    tree_key = task_cache_key.GetSubkeyByName(u'Tree')

    if not tasks_key or not tree_key:
      return False

    parser = TaskCacheDataParser(
        debug=self._debug, output_writer=output_writer)

    task_guids = {}
    for subkey in tree_key.GetSubkeys():
      for value_key, id_value in self._GetIdValue(subkey):
        # TODO: improve this check to a regex.
        # The GUID is in the form {%GUID%} and stored an UTF-16 little-endian
        # string and should be 78 bytes in size.

        id_value_data_size = len(id_value.data)
        if id_value_data_size != 78:
          logging.error(u'Unsupported Id value data size: {0:s}.')
          continue

        guid_string = id_value.GetDataAsObject()
        task_guids[guid_string] = value_key.name

    for subkey in tasks_key.GetSubkeys():
      dynamic_info_value = subkey.GetValueByName(u'DynamicInfo')
      if not dynamic_info_value:
        continue

      cached_task = CachedTask()
      cached_task.identifier = subkey.name
      cached_task.name = task_guids.get(subkey.name, subkey.name)

      if self._debug:
        if (task_cache_key.last_written_time and
            task_cache_key.last_written_time.timestamp):
          date_string = parser.CopyFiletimeToString(
              task_cache_key.last_written_time.timestamp)
          output_writer.WriteValue(u'Last written time', date_string)

        output_writer.WriteValue(u'Task', cached_task.name)
        output_writer.WriteValue(u'Identifier', cached_task.identifier)
        output_writer.WriteText(u'')

      try:
        parser.ParseDynamicInfo(dynamic_info_value.data, cached_task)
      except errors.ParseError as exception:
        if not dynamic_info_size_error_reported:
          logging.error(exception)
          dynamic_info_size_error_reported = True
        continue

      output_writer.WriteCachedTask(cached_task)

    return True
