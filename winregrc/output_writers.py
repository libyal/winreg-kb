# -*- coding: utf-8 -*-
"""Output writer."""

import abc

from dfdatetime import fat_date_time as dfdatetime_fat_date_time
from dfdatetime import filetime as dfdatetime_filetime

from winregrc import hexdump


class OutputWriter(object):
  """Output writer interface."""

  # Note that redundant-returns-doc is broken for pylint 1.7.x
  # pylint: disable=redundant-returns-doc

  _HEXDUMP_CHARACTER_MAP = [
      '.' if byte < 0x20 or byte > 0x7e else chr(byte) for byte in range(256)]

  def _FormatDataInHexadecimal(self, data):
    """Formats data in a hexadecimal representation.

    Args:
      data (bytes): data.

    Returns:
      str: hexadecimal representation of the data.
    """
    in_group = False
    previous_hexadecimal_string = None

    lines = []
    data_size = len(data)
    for block_index in range(0, data_size, 16):
      data_string = data[block_index:block_index + 16]

      hexadecimal_byte_values = []
      printable_values = []
      for byte_value in data_string:
        if isinstance(byte_value, str):
          byte_value = ord(byte_value)

        hexadecimal_byte_values.append(f'{byte_value:02x}')

        printable_value = self._HEXDUMP_CHARACTER_MAP[byte_value]
        printable_values.append(printable_value)

      remaining_size = 16 - len(data_string)
      if remaining_size == 0:
        whitespace = ''
      elif remaining_size >= 8:
        whitespace = ' ' * ((3 * remaining_size) - 1)
      else:
        whitespace = ' ' * (3 * remaining_size)

      hexadecimal_string_part1 = ' '.join(hexadecimal_byte_values[0:8])
      hexadecimal_string_part2 = ' '.join(hexadecimal_byte_values[8:16])
      hexadecimal_string = (
          f'{hexadecimal_string_part1:s}  {hexadecimal_string_part2:s}'
          f'{whitespace:s}')

      if (previous_hexadecimal_string is not None and
          previous_hexadecimal_string == hexadecimal_string and
          block_index + 16 < data_size):

        if not in_group:
          in_group = True

          lines.append('...')

      else:
        printable_string = ''.join(printable_values)

        lines.append(
            f'0x{block_index:08x}  {hexadecimal_string:s}  '
            f'{printable_string:s}')

        in_group = False
        previous_hexadecimal_string = hexadecimal_string

    lines.extend(['', ''])
    return '\n'.join(lines)

  def _FormatFATDateTimeValue(self, value):
    """Formats a FAT date time value.

    Args:
      value (int): FAT date time value.

    Returns:
      str: date time string.
    """
    if not value:
      date_time_string = 'Not set (0)'
    else:
      date_time = dfdatetime_fat_date_time.FATDateTime(fat_date_time=value)
      date_time_string = date_time.CopyToDateTimeString()
      if not date_time_string:
        date_time_string = f'0x{value:04x}'

    return date_time_string

  def _FormatFiletimeValue(self, value):
    """Formats a FILETIME timestamp value.

    Args:
      value (int): FILETIME timestamp value.

    Returns:
      str: date time string.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    elif value == 0x7fffffffffffffff:
      date_time_string = 'Never (0x7fffffffffffffff)'
    else:
      date_time = dfdatetime_filetime.Filetime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = f'{date_time_string:s} UTC'
      else:
        date_time_string = f'0x{value:08x}'

    return date_time_string

  @abc.abstractmethod
  def Close(self):
    """Closes the output writer."""

  def DebugPrintData(self, description, data):
    """Prints data for debugging.

    Args:
      description (str): description.
      data (bytes): data.
    """
    self.WriteText(f'{description:s}:\n')

    value_string = self._FormatDataInHexadecimal(data)
    self.WriteText(value_string)

  def DebugPrintValue(self, description, value):
    """Prints a value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    alignment, _ = divmod(len(description), 8)
    alignment_string = '\t' * (8 - alignment + 1)
    self.WriteText(f'{description:s}{alignment_string:s}: {value!s}\n')

  def DebugPrintText(self, text):
    """Prints text for debugging.

    Args:
      text (str): text.
    """
    self.WriteText(text)

  @abc.abstractmethod
  def Open(self):
    """Opens the output writer.

    Returns:
      bool: True if successful or False if not.
    """

  @abc.abstractmethod
  def WriteDebugData(self, description, data):
    """Writes data for debugging.

    Args:
      description (str): description.
      data (bytes): data to write.
    """

  @abc.abstractmethod
  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal.

    Args:
      description (str): description.
      value (int): value to write.
    """

  @abc.abstractmethod
  def WriteFiletimeValue(self, description, value):
    """Writes a FILETIME timestamp value.

    Args:
      description (str): description.
      value (str): value to write.
    """

  @abc.abstractmethod
  def WriteText(self, text):
    """Writes text.

    Args:
      text (str): text to write.
    """

  @abc.abstractmethod
  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description.
      value (str): value to write.
    """


class StdoutOutputWriter(OutputWriter):
  """Stdout output writer."""

  def Close(self):
    """Closes the output writer."""
    return

  def Open(self):
    """Opens the output writer.

    Returns:
      bool: True if successful or False if not.
    """
    return True

  def WriteDebugData(self, description, data):
    """Writes data for debugging.

    Args:
      description (str): description.
      data (bytes): data.
    """
    self.WriteText(description)
    self.WriteText('\n')

    hexdump_text = hexdump.Hexdump(data)
    self.WriteText(hexdump_text)

  def WriteFiletimeValue(self, description, value):
    """Writes a FILETIME timestamp value.

    Args:
      description (str): description.
      value (int): FILETIME timestamp value.
    """
    date_time_string = self._FormatFiletimeValue(value)
    self.WriteValue(description, date_time_string)

  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal.

    Args:
      description (str): description.
      value (int): integer value.
    """
    self.WriteValue(description, f'{value:d}')

  def WriteText(self, text):
    """Writes text.

    Args:
      text (str): text to write.
    """
    print(text, end='')

  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description.
      value (object): value.
    """
    description_no_tabs = description.replace('\t', ' ' * 8)
    alignment, _ = divmod(len(description_no_tabs), 8)
    alignment_string = '\t' * (8 - alignment + 1)
    self.WriteText(f'{description:s}{alignment_string:s}: {value!s}\n')
