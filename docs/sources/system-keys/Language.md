# Language

The language settings are stored in the key:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Nls\Language
```

Values:

Name | Data type | Description
--- | --- | ---
`#` | REG_SZ | The name of the code page National Language Support file (.nls) <br/> Where # is a hexadecimal formatted LCID, e.g. 0409 <br/> Contains "l_intl.nls", which is a reference to "\Windows\System32\l_intl.nls"
Default | REG_SZ | The default system language, contains a hexadecimal formatted LCID
InstallLanguage | REG_SZ | contains a hexadecimal formatted LCID

## Language groups

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Nls\Language Groups
```

