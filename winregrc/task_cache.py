# -*- coding: utf-8 -*-
"""Task Cache collector."""

from __future__ import print_function
import datetime
import logging

import construct

from winregrc import hexdump
from winregrc import interface


class TaskCacheDataParser(object):
  """Class that parses the Task Cache value data."""

  # TODO: implement.


class TaskCacheCollector(interface.WindowsRegistryKeyCollector):
  """Class that defines a Task Cache collector."""

  _DYNAMIC_INFO_STRUCT = construct.Struct(
      u'dynamic_info_record',
      construct.ULInt32(u'unknown1'),
      construct.ULInt64(u'last_registered_time'),
      construct.ULInt64(u'launch_time'),
      construct.ULInt32(u'unknown2'),
      construct.ULInt32(u'unknown3'))

  _DYNAMIC_INFO_STRUCT_SIZE = _DYNAMIC_INFO_STRUCT.sizeof()

  _DYNAMIC_INFO2_STRUCT = construct.Struct(
      u'dynamic_info2_record',
      construct.ULInt32(u'unknown1'),
      construct.ULInt64(u'last_registered_time'),
      construct.ULInt64(u'launch_time'),
      construct.ULInt32(u'unknown2'),
      construct.ULInt32(u'unknown3'),
      construct.ULInt64(u'unknown_time'))

  _DYNAMIC_INFO2_STRUCT_SIZE = _DYNAMIC_INFO2_STRUCT.sizeof()

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

      dynamic_info_value_data = dynamic_info_value.data
      dynamic_info_value_data_size = len(dynamic_info_value_data)

      if self._debug:
        print(u'DynamicInfo value data:')
        print(hexdump.Hexdump(dynamic_info_value_data))

      if dynamic_info_value_data_size == self._DYNAMIC_INFO_STRUCT_SIZE:
        dynamic_info_struct = self._DYNAMIC_INFO_STRUCT.parse(
            dynamic_info_value_data)

      elif dynamic_info_value_data_size == self._DYNAMIC_INFO2_STRUCT_SIZE:
        dynamic_info_struct = self._DYNAMIC_INFO2_STRUCT.parse(
            dynamic_info_value_data)

      else:
        if not dynamic_info_size_error_reported:
          logging.error(
              u'Unsupported DynamicInfo value data size: {0:d}.'.format(
                  dynamic_info_value_data_size))
          dynamic_info_size_error_reported = True
        continue

      last_registered_time = dynamic_info_struct.get(u'last_registered_time')
      launch_time = dynamic_info_struct.get(u'launch_time')
      unknown_time = dynamic_info_struct.get(u'unknown_time')

      if self._debug:
        print(u'Unknown1\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            dynamic_info_struct.get(u'unknown1')))

        timestamp = last_registered_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        print(u'Last registered time\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
            date_string, last_registered_time))

        timestamp = launch_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        print(u'Launch time\t\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
            date_string, launch_time))

        print(u'Unknown2\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            dynamic_info_struct.get(u'unknown2')))
        print(u'Unknown3\t\t\t\t\t\t\t\t: 0x{0:08x}'.format(
            dynamic_info_struct.get(u'unknown3')))

        if dynamic_info_value_data_size == self._DYNAMIC_INFO2_STRUCT_SIZE:
          timestamp = unknown_time // 10
          date_string = (datetime.datetime(1601, 1, 1) +
                         datetime.timedelta(microseconds=timestamp))

          print(u'Unknown time\t\t\t\t\t\t\t\t: {0!s} (0x{1:08x})'.format(
              date_string, unknown_time))

        print(u'')

      name = task_guids.get(subkey.name, subkey.name)

      output_writer.WriteText(u'Task: {0:s}'.format(name))
      output_writer.WriteText(u'ID: {0:s}'.format(subkey.name))

      if (task_cache_key.last_written_time and
          task_cache_key.last_written_time.timestamp):
        timestamp = task_cache_key.last_written_time.timestamp // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        output_writer.WriteText(u'Last written time: {0!s}'.format(date_string))

      if last_registered_time:
        # Note this is likely either the last registered time or
        # the update time.
        timestamp = last_registered_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        output_writer.WriteText(u'Last registered time: {0!s}'.format(
            date_string))

      if launch_time:
        # Note this is likely the launch time.
        timestamp = launch_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        output_writer.WriteText(u'Launch time: {0!s}'.format(date_string))

      if unknown_time:
        timestamp = unknown_time // 10
        date_string = (datetime.datetime(1601, 1, 1) +
                       datetime.timedelta(microseconds=timestamp))

        output_writer.WriteText(u'Unknown time: {0!s}'.format(date_string))

      output_writer.WriteText(u'')

    return True
