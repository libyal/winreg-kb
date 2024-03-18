# -*- coding: utf-8 -*-
"""Windows Registry volume scanner."""

from dfimagetools import windows_registry

from dfvfs.helpers import command_line as dfvfs_command_line
from dfvfs.helpers import volume_scanner as dfvfs_volume_scanner
from dfvfs.lib import definitions as dfvfs_definitions
from dfvfs.lib import errors as dfvfs_errors
from dfvfs.resolver import resolver as dfvfs_resolver

from dfwinreg import interface as dfwinreg_interface
from dfwinreg import registry as dfwinreg_registry


class VolumeScannerOptions(dfvfs_volume_scanner.VolumeScannerOptions):
  """Volume scanner options.

  Attributes:
    credentials (list[tuple[str, str]]): credentials, per type, to unlock
        volumes.
    partitions (list[str]): partition identifiers.
    scan_mode (str): mode that defines how the VolumeScanner should scan
        for volumes and snapshots.
    snapshots (list[str]): snapshot identifiers.
    username (str): username.
    volumes (list[str]): volume identifiers, e.g. those of an APFS or LVM
        volume system.
  """

  def __init__(self):
    """Initializes volume scanner options."""
    super(VolumeScannerOptions, self).__init__()
    self.username = None


class SingleFileWindowsRegistryFileReader(
    dfwinreg_interface.WinRegistryFileReader):
  """Single file Windows Registry file reader."""

  def __init__(self, path):
    """Initializes a single file Windows Registry file reader.

    Args:
      path (str): path of the Windows Registry file.
    """
    super(SingleFileWindowsRegistryFileReader, self).__init__()
    self._path = path

  def Open(self, path, ascii_codepage='cp1252'):
    """Opens the Windows Registry file specified by the path.

    Args:
      path (str): path of the Windows Registry file. The path is a Windows path
          relative to the root of the file system that contains the specific
          Windows Registry file. E.g. C:\\Windows\\System32\\config\\SYSTEM
      ascii_codepage (Optional[str]): ASCII string codepage.

    Returns:
      WinRegistryFile: Windows Registry file or None if the file cannot
          be opened.
    """
    file_object = open(self._path, 'rb')  # pylint: disable=consider-using-with
    if file_object is None:
      return None

    try:
      signature = file_object.read(4)

      if signature == b'regf':
        registry_file = windows_registry.REGFWindowsRegistryFile(
            ascii_codepage=ascii_codepage)
      else:
        registry_file = windows_registry.CREGWindowsRegistryFile(
            ascii_codepage=ascii_codepage)

      # Note that registry_file takes over management of file_object.
      registry_file.Open(file_object)

    except IOError:
      file_object.close()
      return None

    return registry_file


class WindowsRegistryVolumeScanner(dfvfs_volume_scanner.WindowsVolumeScanner):
  """Windows Registry volume scanner.

  Attributes:
    registry (dfwinreg.WinRegistry): Windows Registry.
  """

  def __init__(self, mediator=None):
    """Initializes a Windows Registry collector.

    Args:
      mediator (Optional[dfvfs.VolumeScannerMediator]): a volume scanner
          mediator.
    """
    super(WindowsRegistryVolumeScanner, self).__init__(mediator=mediator)
    self._single_file = False
    self._users_path = False

    self.registry = None

  def _GetUsername(self, options):
    """Determines the username.

    Args:
      options (VolumeScannerOptions): volume scanner options.

    Returns:
      str: username or None if not available.

    Raises:
      ScannerError: if the scanner does not know how to proceed.
      UserAbort: if the user requested to abort.
    """
    usernames = []

    # TODO: handle alternative users path locations
    self._users_path = '\\Users'
    users_path_spec = self._path_resolver.ResolvePath(self._users_path)
    if not users_path_spec:
      self._users_path = '\\Documents and Settings'
      users_path_spec = self._path_resolver.ResolvePath(self._users_path)

    if users_path_spec:
      users_file_entry = dfvfs_resolver.Resolver.OpenFileEntry(
          users_path_spec)
      for sub_file_entry in users_file_entry.sub_file_entries:
        if sub_file_entry.IsDirectory():
          usernames.append(sub_file_entry.name)

    if not usernames:
      return None

    # Handle options without an username.
    if hasattr(options, 'username'):
      if options.username == ['none']:
        return None

      if options.username:
        if options.username in usernames:
          return options.username

    elif len(usernames) == 1:
      return usernames[0]

    if not self._mediator:
      raise dfvfs_errors.ScannerError(
          'Unable to proceed. Found user profile paths but no mediator to '
          'determine which user to select.')

    try:
      username = self._mediator.GetUsername(usernames)

    except KeyboardInterrupt:
      raise dfvfs_errors.UserAbort('Volume scan aborted.')

    return username

  def IsSingleFileRegistry(self):
    """Determines if the Registry consists of a single file.

    Returns:
      bool: True if the Registry consists of a single file.
    """
    return self._single_file

  def ScanForWindowsVolume(self, source_path, options=None):
    """Scans for a Windows volume.

    Args:
      source_path (str): source path.
      options (Optional[VolumeScannerOptions]): volume scanner options. If None
          the default volume scanner options are used, which are defined in the
          VolumeScannerOptions class.

    Returns:
      bool: True if a Windows volume was found.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within
          the source file is not supported.
    """
    result = super(WindowsRegistryVolumeScanner, self).ScanForWindowsVolume(
        source_path, options=options)

    registry_file_reader = None
    if self._source_type == dfvfs_definitions.SOURCE_TYPE_FILE:
      self._single_file = True

      registry_file_reader = SingleFileWindowsRegistryFileReader(source_path)

    elif result:
      username = self._GetUsername(options)
      if username:
        self._path_resolver.SetEnvironmentVariable(
            'UserProfile', f'{self._users_path:s}\\{username:s}')

      registry_file_reader = (
          windows_registry.StorageMediaImageWindowsRegistryFileReader(
              self._file_system, self._path_resolver))

    if registry_file_reader:
      self.registry = dfwinreg_registry.WinRegistry(
          registry_file_reader=registry_file_reader)

    return bool(registry_file_reader)


class WindowsRegistryVolumeScannerMediator(
    dfvfs_command_line.CLIVolumeScannerMediator):
  """Windows Registry volume scanner mediator."""

  _USER_PROMPT_USERNAMES = (
      'Please specify the username that should be processed. Note that you can '
      'abort with Ctrl^C.')

  def GetUsername(self, usernames):
    """Retrieves a username.

    This method can be used to prompt the user to provide a username.

    Args:
      usernames (list[str]): usernames.

    Returns:
      str: selected username or None.
    """
    # TODO: use user artifact
    self._PrintUsernames(usernames)

    while True:
      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(self._USER_PROMPT_USERNAMES)
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\nUsername: ')

      try:
        selected_username = self._input_reader.Read()
        selected_username = selected_username.strip()
        if selected_username in usernames:
          break
      except ValueError:
        pass

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(
          'Unsupported username, please try again or abort with Ctrl^C.')
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\n')

    return selected_username

  def _PrintUsernames(self, usernames):
    """Prints an overview of usernames.

    Args:
      usernames (list[str]): usernames.

    Raises:
      ScannerError: if a username cannot be resolved.
    """
    header = 'The following usernames were found:\n'
    self._output_writer.Write(header)

    column_names = ['Username', 'Profile path']
    table_view = dfvfs_command_line.CLITabularTableView(
        column_names=column_names)

    for username in sorted(usernames, key=lambda username: username.lower()):
      # TODO: use user artifact
      table_view.AddRow([username, f'C:\\Users\\{username:s}'])

    self._output_writer.Write('\n')
    table_view.Write(self._output_writer)
