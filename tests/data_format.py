# -*- coding: utf-8 -*-
"""Tests for binary data format and file."""

from __future__ import unicode_literals

import io
import unittest

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps
from dtfabric.runtime import fabric as dtfabric_fabric

from winregrc import data_format
from winregrc import errors

from tests import test_lib


class ErrorBytesIO(io.BytesIO):
  """Bytes IO that errors."""

  # The following methods are part of the file-like object interface.
  # pylint: disable=invalid-name

  def read(self, size=None):  # pylint: disable=unused-argument
    """Reads bytes.

    Args:
      size (Optional[int]): number of bytes to read, where None represents
          all remaining bytes.

    Returns:
      bytes: bytes read.

    Raises:
      IOError: for testing.
    """
    raise IOError('Unable to read for testing purposes.')


class ErrorDataTypeMap(dtfabric_data_maps.DataTypeMap):
  """Data type map that errors."""

  def FoldByteStream(self, unused_mapped_value, **unused_kwargs):
    """Folds the data type into a byte stream.

    Args:
      mapped_value (object): mapped value.

    Returns:
      bytes: byte stream.

    Raises:
      FoldingError: if the data type definition cannot be folded into
          the byte stream.
    """
    raise dtfabric_errors.FoldingError(
        'Unable to fold to byte stream for testing purposes.')

  def MapByteStream(self, unused_byte_stream, **unused_kwargs):
    """Maps the data type on a byte stream.

    Args:
      byte_stream (bytes): byte stream.

    Returns:
      object: mapped value.

    Raises:
      dtfabric.MappingError: if the data type definition cannot be mapped on
          the byte stream.
    """
    raise dtfabric_errors.MappingError(
        'Unable to map byte stream for testing purposes.')


class BinaryDataFormatTest(test_lib.BaseTestCase):
  """Binary data format tests."""

  # pylint: disable=protected-access

  _DATA_TYPE_FABRIC_DEFINITION = b"""\
name: uint32
type: integer
attributes:
  format: unsigned
  size: 4
  units: bytes
---
name: point3d
type: structure
attributes:
  byte_order: little-endian
members:
- name: x
  data_type: uint32
- name: y
  data_type: uint32
- name: z
  data_type: uint32
---
name: shape3d
type: structure
attributes:
  byte_order: little-endian
members:
- name: number_of_points
  data_type: uint32
- name: points
  type: sequence
  element_data_type: point3d
  number_of_elements: shape3d.number_of_points
"""

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _POINT3D = _DATA_TYPE_FABRIC.CreateDataTypeMap('point3d')

  _POINT3D_SIZE = _POINT3D.GetByteSize()

  _SHAPE3D = _DATA_TYPE_FABRIC.CreateDataTypeMap('shape3d')

  def testDebugPrintData(self):
    """Tests the _DebugPrintData function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    test_format._DebugPrintData('Description', data)

    expected_output = [
        'Description:\n',
        ('0x00000000  00 01 02 03 04 05 06                              '
         '.......\n\n')]
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintDecimalValue(self):
    """Tests the _DebugPrintDecimalValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintDecimalValue('Description', 1)

    expected_output = ['Description\t\t\t\t\t\t\t\t: 1\n']
    self.assertEqual(output_writer.output, expected_output)

  # TODO add tests for _DebugPrintFiletimeValue

  def testDebugPrintValue(self):
    """Tests the _DebugPrintValue function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintValue('Description', 'Value')

    expected_output = ['Description\t\t\t\t\t\t\t\t: Value\n']
    self.assertEqual(output_writer.output, expected_output)

  def testDebugPrintText(self):
    """Tests the _DebugPrintText function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        output_writer=output_writer)

    test_format._DebugPrintText('Text')

    expected_output = ['Text']
    self.assertEqual(output_writer.output, expected_output)

  def testFormatDataInHexadecimal(self):
    """Tests the _FormatDataInHexadecimal function."""
    test_format = data_format.BinaryDataFormat()

    data = b'\x00\x01\x02\x03\x04\x05\x06'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06                              '
        '.......\n'
        '\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09                    '
        '..........\n'
        '\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

    data = (
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
        b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f')
    expected_formatted_data = (
        '0x00000000  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '...\n'
        '0x00000020  00 01 02 03 04 05 06 07  08 09 0a 0b 0c 0d 0e 0f  '
        '................\n'
        '\n')
    formatted_data = test_format._FormatDataInHexadecimal(data)
    self.assertEqual(formatted_data, expected_formatted_data)

  # TODO: add tests for _GetDataTypeMap
  # TODO: add tests for _ReadDefinitionFile

  def testReadStructureFromByteStream(self):
    """Tests the _ReadStructureFromByteStream function."""
    output_writer = test_lib.TestOutputWriter()
    test_format = data_format.BinaryDataFormat(
        debug=True, output_writer=output_writer)

    test_format._ReadStructureFromByteStream(
        b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0,
        self._POINT3D, 'point3d')

    # Test with missing byte stream.
    with self.assertRaises(ValueError):
      test_format._ReadStructureFromByteStream(
          None, 0, self._POINT3D, 'point3d')

    # Test with missing data map type.
    with self.assertRaises(ValueError):
      test_format._ReadStructureFromByteStream(
          b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0, None,
          'point3d')

    # Test with data type map that raises an dtfabric.MappingError.
    data_type_map = ErrorDataTypeMap(None)

    with self.assertRaises(errors.ParseError):
      test_format._ReadStructureFromByteStream(
          b'\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00', 0,
          data_type_map, 'point3d')


if __name__ == '__main__':
  unittest.main()
