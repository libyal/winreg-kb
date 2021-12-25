# Moint points

## MountPoints

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints
```

Seen on:

* Windows 2000

Sub keys:

Name | Description
--- | ---
%NAME% | Where %NAME% contains the name of the mount point (or drive mapping).

Where the following forms of %NAME% have been observed:

* Drive letter, for example "C"

### MountPoints name sub key

Sub keys:

Name | Description
--- | ---
`_Autorun` |
`_DIL` |
`_LabelFromReg` |

Values:

Value | Data type | Description
--- | --- | ---
`_UB` | REG_BINARY | 
BaseClass | REG_SZ | 
Version | REG_DWORD | 

## MountPoints2

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2
```

Seen on:

* Windows XP
* Windows 2003
* Windows Vista
* Windows 2008
* Windows 7
* Windows 8.0
* Windows 8.1
* Windows 10

Sub keys:

Name | Description
--- | ---
CPC | (Introduced in Windows Vista?)
CPC\LocalMOF | (Introduced in Windows 7?)
CPC\Volume | (Introduced in Windows Vista?)
%NAME% | Where %NAME% contains the name of the mount point (or drive mapping).

Where the following variants of %NAME% have been observed:

* Drive letter, for example "C"
* Volume identifier (GUID), for example "{01234567-89ab-cdef-0123-456789abcdef}"
* UNC path, for example "##1.2.3.4#username"

### MountPoints2 name sub key

Sub keys:

Name | Description
--- | ---
`_Autorun` |
`_Autorun\Action` |
`_Autorun\DefaultIcon` |
`_Autorun\DefaultLabel` |
Shell |
Shell\Autoplay |
Shell\Autoplay\DropTarget |
Shell\AutoRun |
Shell\AutoRun\Command |

Values:

Value | Data type | Description
--- | --- | ---
BaseClass | REG_SZ | 

