# -*- coding: utf-8 -*-
"""Function to provide hexadecimal representation of data."""


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
      if isinstance(byte_value, str):
        byte_value = ord(byte_value)

      hexadecimal_byte_values.append(f'{byte_value:02x}')

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
          f'0x{block_index:08x}  {hexadecimal_string:s}  {printable_string:s}')

      in_group = False
      previous_hexadecimal_string = hexadecimal_string

  lines.extend(['', ''])
  return '\n'.join(lines)
