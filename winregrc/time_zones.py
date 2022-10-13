# -*- coding: utf-8 -*-
"""Windows time zones collector."""

from winregrc import data_format
from winregrc import errors
from winregrc import interface


class TimeZone(object):
  """Time zone.

  Attributes:
    localized_name (str): localized name.
    name (str): name.
    offset (int): time zone offset in number of minutes from UTC.
  """

  def __init__(self, name):
    """Initializes a time zone.

    Args:
      name (str): name.
    """
    super(TimeZone, self).__init__()
    self.localized_name = None
    self.name = name
    self.offset = 0


class TimeZoneInformationDataParser(data_format.BinaryDataFormat):
  """Time Zone Information (TZI) data parser."""

  _DEBUG_INFO_TZI_RECORD = [
      ('bias', 'Bias', '_FormatIntegerAsDecimal'),
      ('standard_bias', 'Standard bias', '_FormatIntegerAsDecimal'),
      ('daylight_bias', 'Daylight bias', '_FormatIntegerAsDecimal'),
      ('standard_date', 'Standard date', '_FormatSystemTime'),
      ('daylight_date', 'Daylight date', '_FormatSystemTime')]

  _DEFINITION_FILE = 'time_zone_information.yaml'

  _MONTHS = [
      '', 'January', 'February', 'March', 'April', 'May', 'June', 'July',
      'August', 'September', 'October', 'November', 'December']

  _OCCURANCE = ['', '1st', '2nd', '3rd', '4th', 'last']

  _WEEKDAYS = [
      'Sunday', 'Monday', 'Tuesday', 'Wednessday', 'Thursday', 'Friday',
      'Saturday']

  def _FormatSystemTime(self, systemtime):
    """Formats a SYSTEMTIME structure.

    Args:
      systemtime (system_time): SYSTEMTIME structure.

    Returns:
      str: formatted SYSTEMTIME structure.
    """
    if systemtime.month and systemtime.day_of_month:
      occurance = self._OCCURANCE[systemtime.day_of_month]
      weekday = self._WEEKDAYS[systemtime.weekday]
      month = self._MONTHS[systemtime.month]

      if not systemtime.year:
        return (f'{occurance:s} {weekday:s} of {month:s} at '
                f'{systemtime.hours:02d}:{systemtime.minutes:02d}')

      return (f'{occurance:s} {weekday:s} of {month:s} in {systemtime.year:s} '
              f'at {systemtime.hours:02d}:{systemtime.minutes:02d}')

    return 'Not set'

  def ParseTZIValue(self, value_data, time_zone):
    """Parses the TZI value data.

    Args:
      value_data (bytes): TZI value data.
      time_zone (TimeZone): time zone.

    Raises:
      ParseError: if the value data could not be parsed.
    """
    data_type_map = self._GetDataTypeMap('tzi_record')

    try:
      tzi_record = self._ReadStructureFromByteStream(
          value_data, 0, data_type_map, 'TZI record')
    except (ValueError, errors.ParseError) as exception:
      raise errors.ParseError(
          f'Unable to parse TZI record value with error: {exception!s}')

    if self._debug:
      self._DebugPrintStructureObject(tzi_record, self._DEBUG_INFO_TZI_RECORD)

    if tzi_record.standard_bias:
      time_zone.offset = tzi_record.standard_bias
    else:
      time_zone.offset = tzi_record.bias


class TimeZonesCollector(interface.WindowsRegistryKeyCollector):
  """Windows time zones collector."""

  _TIME_ZONES_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\'
      'Time Zones')

  def Collect(self, registry, output_writer):
    """Collects the time zones.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the time zones key was found, False if not.
    """
    time_zones_key = registry.GetKeyByPath(self._TIME_ZONES_KEY_PATH)
    if not time_zones_key:
      return False

    time_zone_information_parser = TimeZoneInformationDataParser(
        debug=self._debug, output_writer=output_writer)

    for subkey in time_zones_key.GetSubkeys():
      time_zone = TimeZone(subkey.name)

      if self._debug and output_writer:
        output_writer.DebugPrintValue('Name', subkey.name)

        string = self._GetValueFromKey(subkey, 'Display')
        if string is not None:
          output_writer.DebugPrintValue('Display', string)

        string = self._GetValueFromKey(subkey, 'Dlt')
        if string is not None:
          output_writer.DebugPrintValue('Dlt', string)

        string = self._GetValueFromKey(subkey, 'Std')
        if string is not None:
          output_writer.DebugPrintValue('Std', string)

        string = self._GetValueFromKey(subkey, 'MapID')
        if string is not None:
          output_writer.DebugPrintValue('MapID', string)

        string = self._GetValueFromKey(subkey, 'MUI_Display')
        if string is not None:
          output_writer.DebugPrintValue('MUI_Display', string)

        string = self._GetValueFromKey(subkey, 'MUI_Dlt')
        if string is not None:
          output_writer.DebugPrintValue('MUI_Dlt', string)

        string = self._GetValueFromKey(subkey, 'MUI_Std')
        if string is not None:
          output_writer.DebugPrintValue('MUI_Std', string)

        data = self._GetValueDataFromKey(subkey, 'Index')
        if data is not None:
          output_writer.DebugPrintData('Index', data)

      data = self._GetValueDataFromKey(subkey, 'TZI')
      if self._debug and output_writer and data is not None:
        output_writer.DebugPrintData('TZI', data)

      time_zone_information_parser.ParseTZIValue(data, time_zone)

      if self._debug and output_writer:
        output_writer.DebugPrintText('\n')

      output_writer.WriteTimeZone(time_zone)

    return True
