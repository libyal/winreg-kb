# -*- coding: utf-8 -*-
"""Windows type libraries collector."""

from winregrc import interface


class TypeLibrary(object):
  """Type library.

  Attributes:
    description (str): description.
    guid (str): identifier.
    typelib_filename (str): typelib_filename.
    version (str): version.
  """

  def __init__(self, guid, version, description, typelib_filename):
    """Initializes a type library.

    Args:
      guid (str): identifier.
      version (str): version.
      description (str): description.
      typelib_filename (str): typelib_filename.
    """
    super(TypeLibrary, self).__init__()
    self.description = description
    self.guid = guid
    self.typelib_filename = typelib_filename
    self.version = version


class TypeLibrariesCollector(interface.WindowsRegistryKeyCollector):
  """Windows type libraries collector."""

  _TYPE_LIBRARIES_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Classes\\TypeLib')

  def Collect(self, registry, output_writer):
    """Collects the type libraries.

    Args:
      registry (dfwinreg.WinRegistry): Windows Registry.
      output_writer (OutputWriter): output writer.

    Returns:
      bool: True if the type libraries key was found, False if not.
    """
    type_libraries_key = registry.GetKeyByPath(
        self._TYPE_LIBRARIES_KEY_PATH)
    if not type_libraries_key:
      return False

    for type_library_key in type_libraries_key.GetSubkeys():
      guid = type_library_key.name.lower()

      for subkey in type_library_key.GetSubkeys():
        if subkey.name in (u'FLAGS', u'HELPDIR'):
          continue

        description = self._GetValueAsStringFromKey(
            subkey, u'')

        language_key = None
        for lcid in (u'0', u'409'):
          language_key = subkey.GetSubkeyByName(lcid)
          if language_key:
            break

        if not language_key:
          for language_key in subkey.GetSubkeys():
            if language_key.name not in (u'FLAGS', u'HELPDIR'):
              break

        platform_key = None
        if language_key:
          for platform in (u'win32', ):
            platform_key = language_key.GetSubkeyByName(platform)
            if platform_key:
              break

          if not platform_key:
            platform_key = language_key.GetSubkeyByIndex(0)

        typelib_filename = self._GetValueAsStringFromKey(
            platform_key, u'')

        type_library = TypeLibrary(
            guid, subkey.name, description, typelib_filename)
        output_writer.WriteTypeLibrary(type_library)

    return False
