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

### LocalizedName value data

The LocalizedName value contains a localized version of the folder name, e.g.
on Windows XP the folder identifier key:

```
HKEY_CLASSES_ROOT\CLSID\{450d8fba-ad25-11d0-98a8-0800361b1103}
```

Has a LocalizedString value with the following data:

```
@%SystemRoot%\system32\SHELL32.dll,-9227
```

Which is the [MUI Form](https://winreg-kb.readthedocs.io/en/latest/sources/windows-registry/MUI-form.html)
for "My Documents".

## External links

* [libfwsi: Known Folder Identifiers](https://github.com/libyal/libfwsi/wiki/Known-Folder-Identifiers)

