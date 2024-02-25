# -*- coding: utf-8 -*-
"""Windows type libraries collector."""

from winregrc import interface


class TypeLibrary(object):
  """Type library.

  Attributes:
    description (str): description.
    identifier (str): identifier.
    typelib_filename (str): typelib_filename.
    version (str): version.
  """

  def __init__(self, identifier, version, description, typelib_filename):
    """Initializes a type library.

    Args:
      identifier (str): identifier.
      version (str): version.
      description (str): description.
      typelib_filename (str): typelib_filename.
    """
    super(TypeLibrary, self).__init__()
    self.description = description
    self.identifier = identifier
    self.typelib_filename = typelib_filename
    self.version = version


class TypeLibrariesCollector(interface.WindowsRegistryKeyCollector):
  """Windows type libraries collector.

  Attributes:
    type_libraries (list[TypeLibrary]): type libraries.
  """

  _TYPE_LIBRARIES_KEY_PATH = (
      'HKEY_LOCAL_MACHINE\\Software\\Classes\\TypeLib')

  def __init__(self, debug=False, output_writer=None):
    """Initializes a Windows type libraries collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      output_writer (Optional[OutputWriter]): output writer.
    """
    super(TypeLibrariesCollector, self).__init__(debug=debug)
    self._output_writer = output_writer
    self.type_libraries = []

  def Collect(self, registry):  # pylint: disable=arguments-differ
    """Collects the type libraries.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.

    Returns:
      bool: True if the type libraries key was found, False if not.
    """
    type_libraries_key = registry.GetKeyByPath(
        self._TYPE_LIBRARIES_KEY_PATH)
    if not type_libraries_key:
      return False

    for type_library_key in type_libraries_key.GetSubkeys():
      identifier = type_library_key.name.lower()

      for subkey in type_library_key.GetSubkeys():
        if subkey.name in ('FLAGS', 'HELPDIR'):
          continue

        description = self._GetValueFromKey(subkey, '')

        language_key = None
        for lcid in ('0', '409'):
          language_key = subkey.GetSubkeyByName(lcid)
          if language_key:
            break

        if not language_key:
          for language_key in subkey.GetSubkeys():
            if language_key.name not in ('FLAGS', 'HELPDIR'):
              break

        platform_key = None
        if language_key:
          for platform in ('win32', ):
            platform_key = language_key.GetSubkeyByName(platform)
            if platform_key:
              break

          if not platform_key:
            platform_key = language_key.GetSubkeyByIndex(0)

        typelib_filename = self._GetValueFromKey(platform_key, '')

        type_library = TypeLibrary(
            identifier, subkey.name, description, typelib_filename)
        self.type_libraries.append(type_library)

    return True
