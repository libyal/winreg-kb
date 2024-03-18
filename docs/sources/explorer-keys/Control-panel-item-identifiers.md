# Control panel item identifiers

A control panel item identifier is a GUID that identifies a specific control
panel item.

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Explorer\ControlPanel\NameSpace\{%GUID%}
```

Values:

Name | Data type | Description
--- | --- | ---
Category | REG_DWORD | 
(default) | REG_SZ | Module name of the control panel item
PreferredPlan | REG_SZ |

