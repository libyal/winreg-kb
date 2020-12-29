# Windows Registry files

## Windows Registry files - Windows 3.1

On Windows 3.1 the SHCC file format is used to store Windows Registry data.

Paths of known Windows Registry files:

Filename | Path | Description
--- | --- | ---
REG.DAT | %SystemRoot% | Entire registry

## Windows Registry files - Windows 9x/Me

On Windows 9x/Me the [CREG](https://github.com/libyal/libcreg/blob/main/documentation/Windows%209x%20Registry%20File%20(CREG)%20format.asciidoc)
file format is used to store Windows Registry data.

Paths of known Windows Registry files:

Filename | Path | Description | Corresponding Registry Key
--- | --- | --- | ---
SYSTEM.DAT | %SystemRoot% | System specific part of the Registry | `HKEY_LOCAL_MACHINE`
USER.DAT | %SystemRoot% | User specific part of the Registry | `HKEY_USERS`

### Root keys

The root key of both SYSTEM.DAT and USER.DAT contains an empty name string.

## Windows Registry files - Windows NT

On Windows NT and later the [REGF](https://github.com/libyal/libregf/blob/master/documentation/Windows%20NT%20Registry%20File%20(REGF)%20format.asciidoc)
file format is used to store Windows Registry data.

Paths of known Windows Registry files:

Filename | Path | Description | Corresponding Registry Key | Windows version
--- | --- | --- | --- | ---
Amcache.hve | %SystemRoot%\AppCompat\Programs | *TODO* | | 8, 10
BBI | %SystemRoot%\System32\config | *TODO* | | 10
BCD | \Boot (on boot volume) | Boot Configuration Data (BCD) | | Vista, 7
default | %SystemRoot%\System32\config | *TODO* | | NT 4 and later
DRIVERS | %SystemRoot%\System32\config | *TODO* | | 10
ELAM | %SystemRoot%\System32\config | *TODO* | | 10
NTUSER.DAT | %UserProfile% | User specific part of the Registry | `HKEY_CURRENT_USER` | NT 4 and later
NTUSER.MAN | %UserProfile% | Mandatory user specific part of the Registry | | NT 4 and later
SAM | %SystemRoot%\System32\config | Security Account Manager (SAM) part of the Registry | `HKEY_LOCAL_MACHINE\SAM` | NT 4 and later
SECURITY | %SystemRoot%\System32\config | *TODO* | `HKEY_LOCAL_MACHINE\Security` | NT 4 and later
SOFTWARE | %SystemRoot%\System32\config | Software specific part of the Registry | `HKEY_LOCAL_MACHINE\Software` | NT 4 and later
Syscache.hve | System Volume Information | *TODO* | | 7, 2008
SYSTEM | %SystemRoot%\System32\config | System specific part of the Registry | `HKEY_LOCAL_MACHINE\System` | NT 4 and later
userdiff | %SystemRoot%\System32\config | *TODO* | | NT 4 and later
UsrClass.dat | %UserProfile%\Local Settings\Application Data\Microsoft\Windows | File associations and COM Registry entries | | 2000, XP, 2003
UsrClass.dat | %UserProfile%\AppData\Local\Microsoft\Windows | File associations and COM Registry entries | `HKEY_CURRENT_USER\Software\Classes` | Vista and later

*TODO Windows NT 3.1 user specific file under %SystemRoot%\System32\config*
*TODO BCD check Windows 8 and 10*
*TODO userdiff no longer present in Windows 10 ?*
*TODO what about \Windows\profiles\user profile\user.dat ?*
*TODO what about \Windows\System32\SMI\Store\Machine\SCHEMA.DAT (Windows 7)*

### Root keys

The root key names of the different Windows Registry files differ per version
of Windows.

#### Root key - default

*TODO*

#### Root key - NTUSER.DAT

Windows version | Root key name
--- | ---
NT 4 | .Default
2000, XP, 2003 | $$$PROTO.HIV
Vista | CMI-CreateHive{B01E557D-7818-4BA7-9885-E6592398B44E}
2008 | *TODO*
2016 | *TODO*
2019 | *TODO*
7 | CMI-CreateHive{D43B12B8-09B5-40DB-B4F6-F6DFEB78DAEC}
8 | CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}
10 | *TODO*

#### Root key - SAM

Windows version | Root key name
--- | ---
NT4, 2000, XP, 2003 | SAM
Vista | CMI-CreateHive{87E016C8-C811-4B12-9C3A-CDA552F3458D}
2008 | *TODO*
2016 | *TODO*
2019 | *TODO*
7 | CMI-CreateHive{C4E7BA2B-68E8-499C-B1A1-371AC8D717C7}
8 | *TODO*
10 | *TODO*

#### Root key - SECURITY

Windows version | Root key name
--- | ---
NT4, 2000, XP, 2003 | SECURITY
Vista | *TODO*
2008 | *TODO*
2016 | *TODO*
2019 | *TODO*
7 | *TODO*
8 | *TODO*
10 | *TODO*

#### Root key - SOFTWARE

Windows version | Root key name
--- | ---
NT4 | Software
2000, XP | $$$PROTO.HIV
2003 | *TODO*
Vista | CMI-CreateHive{29EE1162-53C9-4474-A2B6-D90A7F6B0A7C}
2008 | *TODO*
2016 | *TODO*
2019 | *TODO*
7 | CMI-CreateHive{199DAFC2-6F16-4946-BF90-5A3FC3A60902}
8 | CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}
10 | *TODO*

#### Root key - Syscache.hve

Windows version | Root key name
--- | ---
7, 2008 | {%GUID%}
2016 | *TODO*
2019 | *TODO*
8 | *TODO*
10 | *TODO*

Where {%GUID%} is a placeholder for a random GUID in the form: {00000000-0000-0000-0000-000000000000}

*Note how consistent are the GUIDs icw CreateHive ?*

#### Root key - SYSTEM

Windows version | Root key name
--- | ---
NT4 | System
2000, XP, 2003 | $$$PROTO.HIV
Vista | CMI-CreateHive{C619BFE8-791A-4B77-922B-F114AB570920}
2008 | *TODO*
7 | CMI-CreateHive{2A7FB991-7BBE-4F9D-B91E-7CB51D4737F5}
8 | CsiTool-CreateHive-{00000000-0000-0000-0000-000000000000}

#### Root key - userdiff

*TODO*

#### Root key - UsrClass.dat

Windows version | Root key name
--- | ---
2000, XP, 2003 | *TODO*
Vista, 7 | %SID%_Classes, where %SID%_Classes is a string of the SID of the user
2008 | *TODO*
2016 | *TODO*
2019 | *TODO*
8 | *TODO*
10 | *TODO*

## Notes

*TODO what about earlier versions of Windows?*

