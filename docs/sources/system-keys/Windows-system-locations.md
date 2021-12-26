# Windows system locations

Windows system locations can be found in the key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion
```

Values:

Name | Data type | Description
--- | --- | ---
CommonFilesDir | REG_SZ | path of the common program files directory, also set in the %CommomProgramFiles% environment variable
CommonFilesDir (x86) | REG_SZ | path of the 32-bit common program directory folder on a 64-bit Windows installation, also set in the %CommomProgramFiles(x86)% environment variable
DevicePath | REG_SZ |
MediaPath | REG_SZ |
MediaPathUnexpanded | REG_SZ |
PF_AccessoriesName | |
ProductId | |
ProgramFilesDir | REG_SZ | path of the "Program Files" directory, also set in the %ProgramFiles% environment variable
ProgramFilesDir (x86) | REG_SZ | path of the 32-bit "Program Files" directory on a 64-bit Windows installation, also set in the %ProgramFiles(x86)% environment variable
SM_AccessoriesName | |
SM_ConfigureProgramsExisted | |
SM_ConfigureProgramsName | |
SM_GamesName | |
WallPaperDir | REG_SZ |

