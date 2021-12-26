# WinRAR

**TODO this page currently contains rough notes, fine tune these**

The WinRAR application uses the following Windows Registry key to store various
user specific information.

```
HKEY_CURRENT_USER\Software\WinRAR\ArcHistory
HKEY_CURRENT_USER\Software\WinRAR\DialogEditHistory\ArcName
HKEY_CURRENT_USER\Software\WinRAR\DialogEditHistory\ExtrPath
```

Values:

Name | Data type | Description
--- | --- | ---
%ITEM% | REG_SZ | Where %ITEM% is a string in the form: "[0-9]+"

