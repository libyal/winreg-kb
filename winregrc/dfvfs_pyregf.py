# -*- coding: utf-8 -*-
"""The pyregf Windows Registry extension for dfVFS."""

import pyregf

from dfdatetime import posix_time

from dfvfs.file_io import file_object_io
from dfvfs.lib import errors
from dfvfs.path import factory
from dfvfs.path import path_spec as dfvfs_path_spec
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper
from dfvfs.vfs import file_entry
from dfvfs.vfs import file_system as dfvfs_file_system
from dfvfs.vfs import vfs_stat

if pyregf.get_version() < '20150411':
  raise ImportWarning(u'dfVFS pyregf requires at least pyregf 20150411.')


# The type indicator definition.
TYPE_INDICATOR_REGF = u'REGF'


# The file-like object.
# TODO: this should likely be a value file-like object.
class RegfFile(file_object_io.FileObjectIO):
  """Class that implements a file-like object using pyregf."""

  def _OpenFileObject(self, path_spec):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A file-like object.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    regf_file = pyregf.file()
    regf_file.open_file_object(file_object)
    return regf_file


# The path specification.
class RegfPathSpec(dfvfs_path_spec.PathSpec):
  """Class that implements the REGF path specification."""

  # Constant to define the default (nameless) value.
  DEFAULT_VALUE_NAME = u''

  TYPE_INDICATOR = TYPE_INDICATOR_REGF

  def __init__(self, key_path=None, value_name=None, parent=None, **kwargs):
    """Initializes the path specification object.

       Note that the REGF path specification must have a parent.

    Args:
      key_path: optional Registry key path.
      value_name: optional Registry value name.
      parent: optional parent path specification (instance of PathSpec).
      kwargs: a dictionary of keyword arguments dependending on the path
              specification

    Raises:
      ValueError: when key_path or parent is not set.
    """
    if not key_path or not parent:
      raise ValueError(u'Missing key path or parent value.')

    super(RegfPathSpec, self).__init__(parent=parent, **kwargs)
    self.key_path = key_path
    self.value_name = value_name

  @property
  def comparable(self):
    """Comparable representation of the path specification."""
    string_parts = []

    string_parts.append(u'key path: {0:s}'.format(self.key_path))
    if self.value_name is not None:
      string_parts.append(u'value name: "{0:s}"'.format(
          self.value_name))

    return self._GetComparable(sub_comparable_string=u', '.join(string_parts))


# The resolver helper.
class RegfResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the REGF volume resolver helper."""

  TYPE_INDICATOR = TYPE_INDICATOR_REGF

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return RegfFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.FileSystem).
    """
    return RegfFileSystem(resolver_context)


# The file entry.
class RegfDirectory(file_entry.Directory):
  """Class that implements a directory object using pyregf."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of RegfPathSpec).
    """
    key_path = getattr(self.path_spec, u'key_path', None)
    value_name = getattr(self.path_spec, u'value_name', None)
    if value_name is None:
      regf_key = self._file_system.GetRegfKey(key_path)

      for regf_subkey in regf_key.GetSubkeys():
        if key_path == self._file_system.PATH_SEPARATOR:
          subkey_path = self._file_system.JoinPath([regf_subkey.name])
        else:
          subkey_path = self._file_system.JoinPath([
              key_path, regf_subkey.name])

        yield RegfPathSpec(
            key_path=subkey_path, parent=self.path_spec.parent)

      for regf_value in regf_key.values:
        yield RegfPathSpec(
            key_path=key_path, value_name=regf_value.name,
            parent=self.path_spec.parent)


class RegfFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pyregf."""

  TYPE_INDICATOR = TYPE_INDICATOR_REGF

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, regf_key=None, regf_value=None):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
      regf_key: optional key object (instance of pyregf.key).
      regf_value: optional value object (instance of pyregf.value).
    """
    super(RegfFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._regf_key = regf_key
    self._regf_value = regf_value

  def _GetDirectory(self):
    """Retrieves the directory object (instance of RegfDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return RegfDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the regf key is missing.
    """
    if not self._regf_key:
      raise errors.BackEndError(u'Missing regf key.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if self._regf_value:
      stat_object.size = self._regf_value.get_data_size()

    # Date and time stat information.
    if self._regf_value:
      timestamp = None
    else:
      timestamp = posix_time.PosixTimestamp.FromFiletime(
          self._regf_key.get_last_written_time_as_integer())

    if timestamp is not None:
      stat_object.mtime = timestamp

    # Ownership and permissions stat information.
    # TODO: add support for security key.

    # File entry type stat information.
    if self._regf_value:
      stat_object.type = stat_object.TYPE_FILE
    else:
      stat_object.type = stat_object.TYPE_DIRECTORY

    # TODO: add support for a link:
    # stat_object.type = stat_object.TYPE_LINK

    # Other stat information.
    stat_object.is_allocated = True

    return stat_object

  # TODO: add support for link property.

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      if self._regf_value:
        self._name = self._regf_value.name
      elif self._regf_key:
        self._name = self._regf_key.name

    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield RegfFileEntry(
            self._resolver_context, self._file_system, path_spec)

  # TODO: implement GetLinkedFileEntry.

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, u'location', None)
    if location is None:
      return
    parent_inode = self._parent_inode
    parent_location = self._file_system.DirnamePath(location)
    if parent_inode is None and parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, u'parent', None)
    # TODO: determine parent_key_path.
    parent_key_path = u''
    path_spec = RegfPathSpec(
        key_path=parent_key_path, parent=parent_path_spec)

    return RegfFileEntry(self._resolver_context, self._file_system, path_spec)


# The file system.
class RegfFileSystem(dfvfs_file_system.FileSystem):
  """Class that implements a file system object using pyregf."""

  LOCATION_ROOT = u'\\'
  PATH_SEPARATOR = u'\\'

  TYPE_INDICATOR = TYPE_INDICATOR_REGF

  def __init__(self, resolver_context):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(RegfFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._regf_base_key = None
    self._regf_file = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._regf_base_key = None

    self._regf_file.close()
    self._regf_file = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    regf_file = pyregf.file()
    regf_file.open_file_object(file_object)
    regf_base_key = self._regf_file.get_root_key()

    self._file_object = file_object
    self._regf_file = regf_file
    self._regf_base_key = regf_base_key

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    key_path = getattr(path_spec, u'key_path', None)
    if not key_path:
      raise errors.PathSpecError(
          u'Unsupported path specification without key path.')

    regf_key = self.GetRegfKey(key_path)
    if not regf_key:
      return False

    value_name = getattr(path_spec, u'value_name', None)
    if value_name is None:
      return True

    regf_value = regf_key.GetValueByName(value_name)
    return regf_value is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    key_path = getattr(path_spec, u'key_path', None)
    if not key_path:
      raise errors.PathSpecError(
          u'Unsupported path specification without key path.')

    value_name = getattr(path_spec, u'value_name', None)

    regf_key = self.GetRegfKey(key_path)
    if not regf_key:
      return

    if value_name is None:
      if key_path == self.LOCATION_ROOT:
        return RegfFileEntry(
            self._resolver_context, self, path_spec, regf_key=regf_key,
            is_root=True)

      return RegfFileEntry(
          self._resolver_context, self, path_spec, regf_key=regf_key)

    regf_value = regf_key.GetValueByName(value_name)
    if not regf_value:
      return

    return RegfFileEntry(
        self._resolver_context, self, path_spec, regf_key=regf_key,
        regf_value=regf_value)

  def GetRegfKey(self, key_path):
    """Retrieves a key.

    Args:
      key_path: the key path relative to the base key.

    Returns:
      The key object (instance of pyregf.key) or None.
    """
    try:
      return self._regf_base_key.get_subkey_by_path(key_path)
    except IOError:
      pass

    return

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    kwargs = {}

    kwargs[u'key_path'] = self.LOCATION_ROOT
    kwargs[u'parent'] = self._path_spec.parent

    path_spec = RegfPathSpec(**kwargs)
    return self.GetFileEntryByPathSpec(path_spec)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(RegfPathSpec)

# Register the resolver helpers with the resolver.
resolver.Resolver.RegisterHelper(RegfResolverHelper())
