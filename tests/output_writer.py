#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the output writer."""

from __future__ import unicode_literals

import unittest

from winregrc import output_writers

from tests import test_lib as shared_test_lib


class StdoutOutputWriterTest(shared_test_lib.BaseTestCase):
  """Tests for the stdout output writer."""

  def testOpenClose(self):
    """Tests the Open and Close functions."""
    test_output_writer = output_writers.StdoutOutputWriter()

    result = test_output_writer.Open()
    self.assertTrue(result)

    test_output_writer.Close()

  def testWriteDebugData(self):
    """Tests the WriteDebugData function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteDebugData('Description', b'DATA')

  def testWriteValue(self):
    """Tests the WriteValue function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteValue('Description', 'Value')

  def testWriteText(self):
    """Tests the WriteText function."""
    test_output_writer = output_writers.StdoutOutputWriter()

    test_output_writer.WriteText('Test')


if __name__ == '__main__':
  unittest.main()
