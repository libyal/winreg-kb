# 7-Zip keys

**TODO this page currently contains rough notes, fine tune these**

The 7-Zip application uses the following Windows Registry key to store various
user specific information.

```
HKEY_CURRENT_USER\Software\7-Zip
```

Sub keys:

Name | Description
--- | ---
FM |

Values:

Value | Data type | Description
--- | --- | ---
Lang | | Language tag, for example "en-US" or "-" if empty.

## 7-Zip FM sub key

Sub keys:

Name | Description
--- | ---
Columns |

Values:

Value | Data type | Description
--- | --- | ---
FlatViewArc# | | Where # is a numeric value e.g. 0 or 1
FolderShortcuts | |
FolderHistory | | Contains a list of UTF-16 little-endian encoded strings with an end-of-string character
ListMode | |
Panels | |
PanelPath# | | Where # is a numeric value e.g. 0 or 1 <br> Contains an UTF-16 little-endian encoded string
Position | |

### 7-Zip FM Columns sub key

Values:

Value | Data type | Description
--- | --- | ---
7-Zip.Rar | REG_BINARY |
7-Zip.7z | REG_BINARY |

