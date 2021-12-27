# Security Accounts Manager (SAM)

The Security Accounts Manager (SAM) is stored in the key:

```
HKEY_LOCAL_MACHINE\SAM\SAM
```

Sub keys:

Name | Description
--- | ---
Domains | Built-in and account domains
RXACT |

Values:

Name | Data type | Description
--- | --- | ---
C | REG_BINARY |

### C value data

The C value data is variable of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | | <mark style="background-color: yellow">**Unknown (Format version?)**</mark>
2 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
4 | 4 | | <mark style="background-color: yellow">**Unknown (empty?)**</mark>
8 | 4 | | Security descriptor data size
12 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
14 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
16 | ... | | Security descriptor data

#### Format version

Value | Description
--- | ---
1 | Used in Windows NT 3.1
2 | Used in Windows NT 3.5
3 | Used in Windows NT 4
6 | Used in Windows 2000
7 | Used in Windows XP and later
9 | Used in Windows Windows 11

