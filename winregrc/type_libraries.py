# -*- coding: utf-8 -*-
"""Windows type libraries collector."""

from dfwinreg import registry

from winregrc import collector


class TypeLibrary(object):
  """Class that defines a type library.

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


class TypeLibrariesCollector(collector.WindowsVolumeCollector):
  """Class that defines a Windows type libraries collector.

  Attributes:
    key_found (bool): True if the Windows Registry key was found.
  """

  _TYPE_LIBRARIES_KEY_PATH = (
      u'HKEY_LOCAL_MACHINE\\Software\\Classes\\TypeLib')

  def __init__(self, debug=False, mediator=None):
    """Initializes a Windows type libraries collector.

    Args:
      debug (Optional[bool]): True if debug information should be printed.
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(TypeLibrariesCollector, self).__init__(mediator=mediator)
    self._debug = debug
    registry_file_reader = collector.CollectorRegistryFileReader(self)
    self._registry = registry.WinRegistry(
        registry_file_reader=registry_file_reader)

    self.key_found = False

  def _GetValueAsStringFromKey(self, key, value_name, default_value=u''):
    """Retrieves a value as a string from the key.

    Args:
      key (dfwinreg.WinRegistryKey): Registry key.
      value_name (str): name of the value.
      default_value (Optional[str]): default value.

    Returns:
      str: value or the default value if not available.
    """
    if not key:
      return default_value

    value = key.GetValueByName(value_name)
    if not value:
      return default_value

    return value.GetDataAsObject()

  def Collect(self, output_writer):
    """Collects the type libraries.

    Args:
      output_writer (OutputWriter): output writer.
    """
    self.key_found = False

    type_libraries_key = self._registry.GetKeyByPath(
        self._TYPE_LIBRARIES_KEY_PATH)
    if not type_libraries_key:
      return

    self.key_found = True

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
