# Volume shadow copies

## FilesNotToSnapshot key

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\BackupRestore\FilesNotToSnapshot
```

Value| Data type| Description
--- | --- | ---
| %NAME% | REG_MULTI_SZ | Where %NAME% contains an array of strings that contain the path of files that are excluded from being added to a volume shadow snapshot. <br/> The files paths can contain the * wildcard.

## External Links

* [Excluding Files from Shadow Copies](https://docs.microsoft.com/en-us/windows/win32/vss/excluding-files-from-shadow-copies)

