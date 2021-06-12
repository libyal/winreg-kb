# -*- coding: utf-8 -*-
"""Output writer."""

import abc

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

        hexadecimal_byte_value = '{0:02x}'.format(byte_value)
        hexadecimal_byte_values.append(hexadecimal_byte_value)

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
      hexadecimal_string = '{0:s}  {1:s}{2:s}'.format(
          hexadecimal_string_part1, hexadecimal_string_part2, whitespace)

      if (previous_hexadecimal_string is not None and
          previous_hexadecimal_string == hexadecimal_string and
          block_index + 16 < data_size):

        if not in_group:
          in_group = True

          lines.append('...')

      else:
        printable_string = ''.join(printable_values)

        lines.append('0x{0:08x}  {1:s}  {2:s}'.format(
            block_index, hexadecimal_string, printable_string))

        in_group = False
        previous_hexadecimal_string = hexadecimal_string

    lines.extend(['', ''])
    return '\n'.join(lines)

  @abc.abstractmethod
  def Close(self):
    """Closes the output writer."""

  def DebugPrintData(self, description, data):
    """Prints data for debugging.

    Args:
      description (str): description.
      data (bytes): data.
    """
    self.WriteText('{0:s}:\n'.format(description))
    self.WriteText(self._FormatDataInHexadecimal(data))

  def DebugPrintValue(self, description, value):
    """Prints a value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    alignment, _ = divmod(len(description), 8)
    alignment = 8 - alignment + 1
    text = '{0:s}{1:s}: {2!s}\n'.format(
        description, '\t' * alignment, value)
    self.WriteText(text)

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
      description (str): description to write.
      data (bytes): data to write.
    """

  @abc.abstractmethod
  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal.

    Args:
      description (str): description to write.
      value (int): value to write.
    """

  @abc.abstractmethod
  def WriteFiletimeValue(self, description, value):
    """Writes a FILETIME timestamp value.

    Args:
      description (str): description to write.
      value (str): value to write.
    """

  @abc.abstractmethod
  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description to write.
      value (str): value to write.
    """

  @abc.abstractmethod
  def WriteText(self, text):
    """Writes text.

    Args:
      text (str): text to write.
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
      description (str): description to write.
      data (bytes): data to write.
    """
    self.WriteText(description)
    self.WriteText('\n')

    hexdump_text = hexdump.Hexdump(data)
    self.WriteText(hexdump_text)

  def WriteFiletimeValue(self, description, value):
    """Writes a FILETIME timestamp value.

    Args:
      description (str): description to write.
      value (str): value to write.
    """
    if value == 0:
      date_time_string = 'Not set (0)'
    elif value == 0x7fffffffffffffff:
      date_time_string = 'Never (0x7fffffffffffffff)'
    else:
      date_time = dfdatetime_filetime.Filetime(timestamp=value)
      date_time_string = date_time.CopyToDateTimeString()
      if date_time_string:
        date_time_string = '{0:s} UTC'.format(date_time_string)
      else:
        date_time_string = '0x{08:x}'.format(value)

    self.WriteValue(description, date_time_string)

  def WriteIntegerValueAsDecimal(self, description, value):
    """Writes an integer value as decimal.

    Args:
      description (str): description to write.
      value (int): value to write.
    """
    value_string = '{0:d}'.format(value)
    self.WriteValue(description, value_string)

  def WriteValue(self, description, value):
    """Writes a value.

    Args:
      description (str): description to write.
      value (object): value to write.
    """
    description_no_tabs = description.replace('\t', ' ' * 8)
    alignment, _ = divmod(len(description_no_tabs), 8)
    alignment = 8 - alignment + 1
    text = '{0:s}{1:s}: {2!s}\n'.format(description, '\t' * alignment, value)
    self.WriteText(text)

  def WriteText(self, text):
    """Writes text.

    Args:
      text (str): text to write.
    """
    print(text, end='')
