# -*- coding: utf-8 -*-
"""Task Cache collector."""

from __future__ import print_function
import datetime
import logging

import construct

from dfwinreg import registry

from winreg_kb import collector
from winreg_kb import hexdump


class TaskCacheCollector(collector.WindowsVolumeCollector):
  """Class that defines a Task Cache collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

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

  def __init__(self, debug=False, mediator=None):
    """Initializes the collector object.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(TaskCacheCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

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

    for sub_key in registry_key.GetSubkeys():
      for value_key, id_value in self._GetIdValue(sub_key):
        yield value_key, id_value

  def Collect(self, output_writer):
    """Collects the Task Cache.

    Args:
      output_writer (OutputWriter): output writer.
    """
    dynamic_info_size_error_reported = False

    self.key_found = False

    task_cache_key = self._registry.GetKeyByPath(self._TASK_CACHE_KEY_PATH)
    if not task_cache_key:
      return

    tasks_key = task_cache_key.GetSubkeyByName(u'Tasks')
    tree_key = task_cache_key.GetSubkeyByName(u'Tree')

    if not tasks_key or not tree_key:
      return

    self.key_found = True

    task_guids = {}
    for sub_key in tree_key.GetSubkeys():
      for value_key, id_value in self._GetIdValue(sub_key):
        # TODO: improve this check to a regex.
        # The GUID is in the form {%GUID%} and stored an UTF-16 little-endian
        # string and should be 78 bytes in size.

        id_value_data_size = len(id_value.data)
        if id_value_data_size != 78:
          logging.error(u'Unsupported Id value data size: {0:s}.')
          continue

        guid_string = id_value.GetDataAsObject()
        task_guids[guid_string] = value_key.name

    for sub_key in tasks_key.GetSubkeys():
      dynamic_info_value = sub_key.GetValueByName(u'DynamicInfo')
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

      name = task_guids.get(sub_key.name, sub_key.name)

      output_writer.WriteText(u'Task: {0:s}'.format(name))
      output_writer.WriteText(u'ID: {0:s}'.format(sub_key.name))

      timestamp = task_cache_key.last_written_time // 10
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
