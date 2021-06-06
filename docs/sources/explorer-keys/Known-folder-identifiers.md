# Known folder identifier keys

A known folder identifier is a GUID that identifies a system folder. It was
introduced in Windows Vista to replace the constant special item identifier list
(CSIDL).

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions
```

Values:

Value | Data type | Description
--- | --- | ---
Name | REG_SZ | Name of the known folder
LocalizedName | REG_SZ | Localized name of the known folder

## External links

* [libfwsi: Known Folder Identifiers](https://github.com/libyal/libfwsi/wiki/Known-Folder-Identifiers)

