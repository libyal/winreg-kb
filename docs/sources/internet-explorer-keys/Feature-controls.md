# Feature controls

Order of application:

1. HKEY_LOCAL_MACHINE policy key (Administrative override)
1. HKEY_CURRENT_USER policy key
1. HKEY_CURRENT_USER preference key
1. HKEY_LOCAL_MACHINE preference key (System default settings)

Note that the location of the HKEY_LOCAL_MACHINE policy and preference key
is dependent on the usage of WoW64 (Windows 32-bit on Windows 64-bit).

Normal:

1. HKEY_LOCAL_MACHINE\\Software\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_CURRENT_USER\\Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl

WoW64:

1. HKEY_LOCAL_MACHINE\\Wow6432Node\\Software\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_CURRENT_USER\\Software\\Policies\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_CURRENT_USER\\Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl
1. HKEY_LOCAL_MACHINE\\Wow6432Node\\Software\\Microsoft\\Internet Explorer\\Main\\FeatureControl

## Security Zones

Value | Description
--- | ---
0 | My Computer
1 | Local Intranet Zone
2 | Trusted sites Zone
3 | Internet Zone
4 | Restricted Sites Zone

Also stored in "Description" Registry value in zone-specific Registry key.

## Local Machine Zone Lockdown

Applies the Lockdown Zones instead of the Zones.

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN\

HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN\

HKEY_CURRENT_USER\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN\
```

Add a REG_DWORD value to this key named for your application (for example, 
MyApplication.exe) and set it to 1. Any other setting for this value will 
disable Local Machine Zone Lockdown for the application.

## Network Protocol Lockdown

```
HKEY_LOCAL_MACHINE\Software\(Policies)\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_PROTOCOL_LOCKDOWN 

HKEY_CURRENT_USER\Software\(Policies)\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_PROTOCOL_LOCKDOWN

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_PROTOCOL_LOCKDOWN
```

## HTML from CD

```
HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN\Settings\LOCALMACHINE_CD_UNLOCK
```

## External Links

* [Introduction to Feature Controls](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537184(v=vs.85))
* [Internet Feature Controls](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/general-info/ee330720(v=vs.85))
* [About URL Security Zones](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/ms537183(v=vs.85))
* [Understanding and Working in Protected Mode Internet Explorer](https://docs.microsoft.com/en-US/troubleshoot/browsers/ie-security-zones-registry-entries)
* [Internet Explorer security zones registry entries for advanced users](https://docs.microsoft.com/en-US/troubleshoot/browsers/ie-security-zones-registry-entries)
* [Internet Explorer Local Machine Zone Lockdown](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc782928(v=ws.10))
* [Internet Explorer Network Protocol Lockdown](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc737488(v=ws.10))
* [Internet Explorer Protected Mode Elevation Policy and Administrative Templates](https://docs.microsoft.com/en-us/archive/blogs/juanand/internet-explorer-protected-mode-elevation-policy-and-administrative-templates)
