# -*- coding: utf-8 -*-
"""Binary data format."""

import os

from dfdatetime import filetime as dfdatetime_filetime

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from winregrc import errors


class BinaryDataFormat(object):
  """Binary data format."""

  # The dtFabric definition file, which must be overwritten by a subclass.
  _DEFINITION_FILE = None

  # Preserve the absolute path value of __file__ in case it is changed
  # at run-time.
  _DEFINITION_FILES_PATH = os.path.dirname(__file__)

  _HEXDUMP_CHARACTER_MAP = [
      '.' if byte < 0x20 or byte > 0x7e else chr(byte) for byte in range(256)]

  def __init__(self, debug=False, output_writer=None):
    """Initializes a binary data format.

    Args:
      debug (Optional[bool]): True if debug information should be written.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(BinaryDataFormat, self).__init__()
    self._data_type_maps = {}
    self._debug = debug
    self._fabric = self._ReadDefinitionFile(self._DEFINITION_FILE)
    self._output_writer = output_writer

  def _DebugPrintData(self, description, data):
    """Prints data for debugging.

    Args:
      description (str): description.
      data (bytes): data.
    """
    if self._output_writer:
      self._output_writer.WriteText(f'{description:s}:\n')

      value_string = self._FormatDataInHexadecimal(data)
      self._output_writer.WriteText(value_string)

  def _DebugPrintDecimalValue(self, description, value):
    """Prints a decimal value for debugging.

    Args:
      description (str): description.
      value (int): value.
    """
    self._DebugPrintValue(description, f'{value:d}')

  def _DebugPrintFiletimeValue(self, description, value):
    """Prints a FILETIME timestamp value for debugging.

    Args:
      description (str): description.
      value (object): value.
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

    self._DebugPrintValue(description, date_time_string)

  def _DebugPrintStructureObject(self, structure_object, debug_info):
    """Prints structure object debug information.

    Args:
      structure_object (object): structure object.
      debug_info (list[tuple[str, str, int]]): debug information.
    """
    text = self._FormatStructureObject(structure_object, debug_info)
    self._output_writer.WriteText(text)

  def _DebugPrintText(self, text):
    """Prints text for debugging.

    Args:
      text (str): text.
    """
    if self._output_writer:
      self._output_writer.DebugPrintText(text)

  def _DebugPrintValue(self, description, value):
    """Prints a value for debugging.

    Args:
      description (str): description.
      value (object): value.
    """
    if self._output_writer:
      text = self._FormatValue(description, value)
      self._output_writer.WriteText(text)

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

  def _FormatIntegerAsDecimal(self, integer):
    """Formats an integer as a decimal.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a decimal.
    """
    return f'{integer:d}'

  def _FormatIntegerAsFiletime(self, integer):
    """Formats an integer as a FILETIME date and time value.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a FILETIME date and time value.
    """
    if integer == 0:
      return 'Not set (0)'

    if integer == 0x7fffffffffffffff:
      return 'Never (0x7fffffffffffffff)'

    date_time = dfdatetime_filetime.Filetime(timestamp=integer)
    date_time_string = date_time.CopyToDateTimeString()
    if not date_time_string:
      return f'0x{integer:08x}'

    return f'{date_time_string:s} UTC'

  def _FormatIntegerAsHexadecimal2(self, integer):
    """Formats an integer as an 2-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an 2-digit hexadecimal.
    """
    return f'0x{integer:02x}'

  def _FormatIntegerAsHexadecimal4(self, integer):
    """Formats an integer as an 4-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an 4-digit hexadecimal.
    """
    return f'0x{integer:04x}'

  def _FormatIntegerAsHexadecimal8(self, integer):
    """Formats an integer as an 8-digit hexadecimal.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as an 8-digit hexadecimal.
    """
    return f'0x{integer:08x}'

  def _FormatStructureObject(self, structure_object, debug_info):
    """Formats a structure object debug information.

    Args:
      structure_object (object): structure object.
      debug_info (list[tuple[str, str, int]]): debug information.

    Returns:
      str: structure object debug information.
    """
    lines = []

    attribute_value = ''
    for attribute_name, description, value_format_callback in debug_info:
      attribute_value = getattr(structure_object, attribute_name, None)
      if attribute_value is None:
        continue

      value_format_function = None
      if value_format_callback:
        value_format_function = getattr(self, value_format_callback, None)
      if value_format_function:
        attribute_value = value_format_function(attribute_value)

      if isinstance(attribute_value, str) and '\n' in attribute_value:
        text = ''
        if description is not None:
          text = f'{description:s}:\n'
        text = ''.join([text, attribute_value])

      else:
        text = self._FormatValue(description, attribute_value)

      lines.append(text)

    if not attribute_value or attribute_value[:-2] != '\n\n':
      lines.append('\n')

    return ''.join(lines)

  def _FormatValue(self, description, value):
    """Formats a value for debugging.

    Args:
      description (str): description.
      value (object): value.

    Returns:
      str: formatted value.
    """
    alignment, _ = divmod(len(description), 8)
    alignment_string = '\t' * (8 - alignment + 1)
    return f'{description:s}{alignment_string:s}: {value!s}\n'

  def _GetDataTypeMap(self, name):
    """Retrieves a data type map defined by the definition file.

    The data type maps are cached for reuse.

    Args:
      name (str): name of the data type as defined by the definition file.

    Returns:
      dtfabric.DataTypeMap: data type map which contains a data type definition,
          such as a structure, that can be mapped onto binary data.
    """
    data_type_map = self._data_type_maps.get(name, None)
    if not data_type_map:
      data_type_map = self._fabric.CreateDataTypeMap(name)
      self._data_type_maps[name] = data_type_map

    return data_type_map

  def _ReadDefinitionFile(self, filename):
    """Reads a dtFabric definition file.

    Args:
      filename (str): name of the dtFabric definition file.

    Returns:
      dtfabric.DataTypeFabric: data type fabric which contains the data format
          data type maps of the data type definition, such as a structure, that
          can be mapped onto binary data or None if no filename is provided.
    """
    if not filename:
      return None

    path = os.path.join(self._DEFINITION_FILES_PATH, filename)
    with open(path, 'rb') as file_object:
      definition = file_object.read()

    return dtfabric_fabric.DataTypeFabric(yaml_definition=definition)

  def _ReadStructureFromByteStream(
      self, byte_stream, file_offset, data_type_map, description, context=None):
    """Reads a structure from a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.
      description (str): description of the structure.
      context (Optional[dtfabric.DataTypeMapContext]): data type map context.

    Returns:
      object: structure values object.

    Raises:
      ParseError: if the structure cannot be read.
      ValueError: if file-like object or data type map is missing.
    """
    if not byte_stream:
      raise ValueError('Missing byte stream.')

    if not data_type_map:
      raise ValueError('Missing data type map.')

    try:
      return data_type_map.MapByteStream(byte_stream, context=context)
    except (dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError) as exception:
      raise errors.ParseError((
          f'Unable to map {description:s} data at offset: 0x{file_offset:08x} '
          f'with error: {exception!s}'))
