# Shell folders

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

