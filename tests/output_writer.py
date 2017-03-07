#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the output writer."""

import unittest

from winregrc import output_writer

from tests import test_lib as shared_test_lib


class StdoutOutputWriterTest(shared_test_lib.BaseTestCase):
  """Tests for the stdout output writer."""

  def testOpenClose(self):
    """Tests the Open and Close functions."""
    test_output_writer = output_writer.StdoutOutputWriter()

    result = test_output_writer.Open()
    self.assertTrue(result)

    test_output_writer.Close()

  def testWriteDebugData(self):
    """Tests the WriteDebugData function."""
    test_output_writer = output_writer.StdoutOutputWriter()

    test_output_writer.WriteDebugData(u'Description', b'DATA')

  def testWriteValue(self):
    """Tests the WriteValue function."""
    test_output_writer = output_writer.StdoutOutputWriter()

    test_output_writer.WriteValue(u'Description', u'Value')

  def testWriteText(self):
    """Tests the WriteText function."""
    test_output_writer = output_writer.StdoutOutputWriter()

    test_output_writer.WriteText(u'Test')


if __name__ == '__main__':
  unittest.main()
