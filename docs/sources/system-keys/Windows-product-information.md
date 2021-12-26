# Windows product information

Windows product information can be found in the key:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion
```

Values:

Name | Data type | Description
--- | --- | ---
BuildLab | REG_SZ |
CSDVersion | REG_SZ | Service pack
CurrentBuild | REG_SZ | Current build (obsolete) e.g. 1.511.1
CurrentBuildNumber | REG_SZ | Current build number e.g. 2600
CurrentType | REG_SZ |
CurrentVersion | REG_SZ | Current major and minor version e.g. 5.1
DigitalProductId | REG_BINARY |
InstallDate | REG_LONG |
LicenseInfo | REG_BINARY |
PathName | REG_SZ | Windows path name e.g. C:\Windows
ProductId | REG_SZ | Product identifier
ProductName | REG_SZ | Product name e.g Microsoft Windows XP
RegDone | |
RegisteredOrganization | REG_SZ | Registered organization
RegisteredOwner | REG_SZ | Registered owner
SoftwareType | REG_SZ | Software type e.g. SYSTEM
SourcePath | REG_SZ |
SubVersionNumber | |
SystemRoot | REG_SZ | The system root also the value of %SystemRoot%

