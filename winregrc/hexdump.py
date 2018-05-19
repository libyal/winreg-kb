# -*- coding: utf-8 -*-
"""Function to provide hexadecimal representation of data."""

from __future__ import unicode_literals

from winregrc import py2to3


_HEXDUMP_CHARACTER_MAP = [
    '.' if byte < 0x20 or byte > 0x7e else chr(byte) for byte in range(256)]


def Hexdump(data):
  """Formats data in a hexadecimal representation.

  Args:
    data (byte): data.

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
      if isinstance(byte_value, py2to3.STRING_TYPES):
        byte_value = ord(byte_value)

      hexadecimal_byte_value = '{0:02x}'.format(byte_value)
      hexadecimal_byte_values.append(hexadecimal_byte_value)

      printable_value = _HEXDUMP_CHARACTER_MAP[byte_value]
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
