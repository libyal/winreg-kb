# -*- coding: utf-8 -*-
"""The error objects."""


class Error(Exception):
  """The error interface."""


class ParseError(Error):
  """Error that is raised when value data cannot be parsed."""
