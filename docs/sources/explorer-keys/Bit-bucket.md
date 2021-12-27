# Bit bucket

The Windows Explorer bit bucket key contains Recycler configuration
properties and information about the Recycler of connected volumes.

```
HKEY_CURRENT_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\BitBucket
```

Seen on Windows 2000, XP and 2003.

Sub keys:

Name | Description
--- | ---
%NAME% | Where %NAME% contains a drive letter, for example "c"

Values:

Name | Data type | Description
--- | --- | ---
NoRecycleFiles | REG_DWORD | 
NukeOnDelete | REG_DWORD | 
Percent | REG_DWORD | 
UseGlobalSettings | REG_DWORD | 

## BitBucket\\%NAME% sub key

Values:

Name | Data type | Description
--- | --- | ---
IsUnicode | REG_DWORD | 
VolumeSerialNumber | REG_DWORD | 

