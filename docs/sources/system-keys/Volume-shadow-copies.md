# Volume shadow copies

## Files Not To Snapshot Key

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\BackupRestore\FilesNotToSnapshot
```

Value| Data type| Description
--- | --- | ---
| %NAME% | REG_MULTI_SZ | Where %NAME% contains an array of strings that contain the path of files that are excluded from being added to a volume shadow snapshot. <br/> The files paths can contain the * wildcard.

### UserProfile environment variable

**TODO: Is this %UserProfile% or should this be $UserProfile$ ? Same for $AllVolumes$.**

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\ProfileList
```

## External Links

* [Excluding Files from Shadow Copies](https://docs.microsoft.com/en-us/windows/win32/vss/excluding-files-from-shadow-copies)

