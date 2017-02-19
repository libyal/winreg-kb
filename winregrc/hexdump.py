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
  for block_index in xrange(0, data_size, 16):
    data_string = data[block_index:block_index + 16]

    hexadecimal_string1 = ' '.join([
        u'{0:02x}'.format(ord(byte_value)) for byte_value in data_string[0:8]])
    hexadecimal_string2 = ' '.join([
        u'{0:02x}'.format(ord(byte_value)) for byte_value in data_string[8:16]])

    printable_string = u''.join([
        _HEXDUMP_CHARACTER_MAP[ord(byte_value)] for byte_value in data_string])

    remaining_size = 16 - len(data_string)
    if remaining_size == 0:
      whitespace = u''
    elif remaining_size >= 8:
      whitespace = ' ' * ((3 * remaining_size) - 1)
    else:
      whitespace = ' ' * (3 * remaining_size)

    hexadecimal_string = u'{0:s}  {1:s}{2:s}'.format(
        hexadecimal_string1, hexadecimal_string2, whitespace)

    if (previous_hexadecimal_string is not None and
        previous_hexadecimal_string == hexadecimal_string and
        block_index + 16 < data_size):

      if not in_group:
        in_group = True

        lines.append('...')

    else:
      lines.append(u'0x{0:08x}  {1:s}  {2:s}'.format(
          block_index, hexadecimal_string, printable_string))

      in_group = False
      previous_hexadecimal_string = hexadecimal_string

  lines.append(u'')
  return u'\n'.join(lines)
