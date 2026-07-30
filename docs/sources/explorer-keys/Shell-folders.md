# Shell folders

## Shell folder identifiers

Shell Folder identifiers are class identifiers with Shell Folder sub key. In
the Windows Registry Some Class identifiers (CLSID) have a ShellFolder sub key
for example:

```
HKEY_LOCAL_MACHINE\Software\CLSID\{%GUID%}\ShellFolder
```

Where {%GUID%} is a GUID in the form: {00000000-0000-0000-0000-000000000000}.

A shell folder can be system or user specific.

System shell folders:

```
HKEY_CURRENT_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
HKEY_CURRENT_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
HKEY_CURRENT_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\Backup
```

WoW64 (Windows 32-bit on Windows 64-bit) system shell folders:

```
HKEY_CURRENT_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
HKEY_CURRENT_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
HKEY_CURRENT_MACHINE\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\Backup
```

Per-user shell folders:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
```

Values:

Name | Data type | Description
--- | --- | ---
%NAME% | REG_SZ or REG_EXPAND_SZ | Path to the corresponding directory


## Shell folder paths

Windows Explorer stores the paths to Windows Explorer folders (or shell folders)
across multiple keys.

Windows 2000 and later:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders\New
HKEY_LOCAL_MACHINE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders
```

Windows NT and earlier:

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
HKEY_LOCAL_MACHINE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders
```

## External links

* [User Shell Folders](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-2000-server/cc962613(v=technet.10))

