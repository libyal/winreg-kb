# Codepage

The codepage settings are stored in the key:

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Nls\CodePage
```

Value | Data type | Description
--- | --- | ---
`#` | REG_SZ | The name of the code page National Language Support file (.nls) <br/> Where # is the code page number, e.g. 1252 <br/> Contains a string with the name of the corresponding file e.g. c_1252.nls
ACP | REG_SZ | The default ANSI (extended ASCII) code page <br/> Contains a string with the number of the corresponding code page e.g. 1252
MACCP | REG_SZ | The default Macintosh code page <br/> Contains a string with the number of the corresponding code page e.g. 1252
OEMCP | REG_SZ | The default OEM code page <br/> Contains a string with the number of the corresponding code page e.g. 1252
OEMHAL | REG_SZ | <mark style="background-color: yellow">**Unknown**</mark> <br/> Contains a string with the name of the corresponding file e.g. vgaoem.fon

