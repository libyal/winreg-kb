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
      self._output_writer.DebugPrintData(description, data)

  def _DebugPrintDecimalValue(self, description, value):
    """Prints a decimal value for debugging.

    Args:
      description (str): description.
      value (int): value.
    """
    value_string = '{0:d}'.format(value)
    self._DebugPrintValue(description, value_string)

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
        date_time_string = '{0:s} UTC'.format(date_time_string)
      else:
        date_time_string = '0x{08:x}'.format(value)

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
      self._output_writer.DebugPrintValue(description, value)

  def _FormatIntegerAsDecimal(self, integer):
    """Formats an integer as a decimal.

    Args:
      integer (int): integer.

    Returns:
      str: integer formatted as a decimal.
    """
    return '{0:d}'.format(integer)

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
        text = '{0:s}:\n{1:s}'.format(description, attribute_value)
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
    alignment = 8 - alignment + 1
    return '{0:s}{1:s}: {2!s}\n'.format(description, '\t' * alignment, value)

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
          'Unable to map {0:s} data at offset: 0x{1:08x} with error: '
          '{2!s}').format(description, file_offset, exception))
