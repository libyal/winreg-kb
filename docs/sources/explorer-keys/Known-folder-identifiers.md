# Known folder identifier keys

A known folder identifier is a GUID that identifies a system folder. It was
introduced in Windows Vista to replace the constant special item identifier list
(CSIDL).

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\FolderDescriptions
```

Values:

Name | Data type | Description
--- | --- | ---
Attributes | REG_DWORD | 
Category | REG_DWORD | 
Name | REG_SZ | Name of the known folder
LocalizedName | REG_EXPAND_SZ | Localized name of the known folder
ParentFolder | REG_SZ | Path of the parent directory known folder, can contain a known folder identifier
PreCreate | REG_DWORD | 
RelativePath | REG_SZ | Relative path of the known folder

## External links

* [libfwsi: Known Folder Identifiers](https://github.com/libyal/libfwsi/wiki/Known-Folder-Identifiers)

