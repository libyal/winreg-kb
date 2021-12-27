# Domains

The Security Accounts Manager (SAM) domains are stored in the key:

```
HKEY_LOCAL_MACHINE\SAM\SAM\Domains
```

Sub keys:

Name | Description
--- | ---
Account | user, group, and local group accounts.
Builtin | (built-in) default local groups, such as the Administrators and Users groups, that are established when the operating system is installed.

Values:

Name | Data type | Description
--- | --- | ---
(default) | |

## Account or Builtin sub key

Sub keys:

Name | Description
--- | ---
Aliases |
Groups |
Users |

Values:

Name | Data type | Description
--- | --- | ---
F | REG_BINARY |
V | REG_BINARY |

### F value data

Offset | Size | Value | Description
--- | --- | --- | ---
0 | ... | | *TODO*

### V value data

The V value data consists of:

* 17 x user information descriptors
  * security descriptor
  * username
  * full name
  * comment
  * user comment
  * <mark style="background-color: yellow">**Unknown**</mark>
  * home directory
  * home directory connect
  * script path
  * profile path
  * workstations
  * hours allowed
  * <mark style="background-color: yellow">**Unknown**</mark>
  * LM hash (LANMAN)
  * NTLM hash
  * <mark style="background-color: yellow">**Unknown**</mark>
  * <mark style="background-color: yellow">**Unknown**</mark>
* user information data

#### User information descriptor

A user information descriptor is 12 byte of size and consists of:

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Data offset <br> The offset is relative to the end of the last user information descriptor
4 | 4 | | Data size
8 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>

## Aliases sub key

Sub keys:

Name | Description
--- | ---
Members |
Names |
%RID% |

Where %RID% is the relative identifier (RID) which corresponds to the last sub authority of the SID.

### Aliases RID sub key

Values:

Name | Data type | Description
--- | --- | ---
C | REG_BINARY |

#### C value data

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | The relative identifier (RID)
4 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
8 | 4 | | Size of unknown data at offset 52
12 | 2 | 2 | <mark style="background-color: yellow">**Unknown: major format version ?**</mark>
14 | 2 | 1 | <mark style="background-color: yellow">**Unknown: minor format version ?**</mark>
16 | 4 | | Name string offset <br> Relative from offset 52
20 | 4 | | Name string size <br> Contains number of bytes
24 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
28 | 4 | | Description string offset <br> Relative from offset 52
32 | 4 | | Description string size <br> Contains number of bytes
36 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
40 | 4 | | SID array offset <br> Relative from offset 52
44 | 4 | | SID array size
48 | 4 | | SID array number of values
52 | ... | | Contains an https://code.google.com/p/libfwnt/wiki/SecurityDescriptor[NT security descriptor]
... | ... | | Name string <br> Contains an UTF-16 little-endian formatted string without end-of-string character <br> The data is stored using 4-byte alignment
... | ... | | Description string <br> Contains an UTF-16 little-endian formatted string without end-of-string character <br> The data is stored using 4-byte alignment
... | ... | | SID array <br> Contains Windows NT Security Identifiers (SIDs)

### Aliases Members sub key

Sub keys:

Name | Description
--- | ---
%SID% |

Where %SID% is the security identifier (SID) in the form of a string e.g. S-1-5.

#### Aliases Members SID sub key

Sub keys:

Name | Description
--- | ---
%RID% |

Where %RID% is the relative identifier (RID) which corresponds to the last sub authority of the SID.

## Groups sub key

Sub keys:

Name | Description
--- | ---
Names |
%RID% |

### C value data

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | 2 | <mark style="background-color: yellow">**Unknown: major format version ?**</mark>
2 | 2 | 1 | <mark style="background-color: yellow">**Unknown: minor format version ?**</mark>
4 | 4 | | The relative identifier (RID)
8 | 20 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
28 | 2 | 2 | <mark style="background-color: yellow">**Unknown: major format version ?**</mark>
30 | 2 | 1 | <mark style="background-color: yellow">**Unknown: minor format version ?**</mark>
32 | 4 | | Name string offset <br> Relative from offset 68
36 | 4 | | Name string size <br> Contains number of bytes
40 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
44 | 4 | | Description string offset <br> Relative from offset 68
48 | 4 | | Description string size <br> Contains number of bytes
52 | 4 | | <mark style="background-color: yellow">**Unknown (empty values)**</mark>
56 | 4 | | Group member array offset <br> Relative from offset 68
60 | 4 | | Group member array size <br> Contains number of bytes
64 | 4 | | Group member array number of values
68 | ... | | Contains a [security descriptor](https://github.com/libyal/libfwnt/blob/main/documentation/Security%20Descriptor.asciidoc)
... | ... | | Name string <br> Contains an UTF-16 little-endian formatted string without end-of-string character <br> The data is stored using 4-byte alignment
... | ... | | Description string <br> Contains an UTF-16 little-endian formatted string without end-of-string character <br> The data is stored using 4-byte alignment
... | ... | | Group member array <br> Contains 4-byte RID values

## Users sub key

Sub keys:

Name | Description
--- | ---
Names |
%RID% |

Where %RID% is the relative identifier (RID) which corresponds to the last sub authority of the SID.

### Users RID sub key

Values:

Name | Data type | Description
--- | --- | ---
F | REG_BINARY |

#### F value data

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 2 | 2 | <mark style="background-color: yellow">**Unknown: major version ?**</mark>
2 | 2 | 2 | <mark style="background-color: yellow">**Unknown: minor version ?**</mark>
4 | 2 | | <mark style="background-color: yellow">**Unknown: Extended data flags ?**</mark>
6 | 2 | | <mark style="background-color: yellow">**Unknown: Extended data size ?**</mark>
8 | 8 | | Last logon date and time (lastLogon) <br> Contains a FILETIME
16 | 8 | | <mark style="background-color: yellow">**Unknown (lastLogoff?)**</mark>
24 | 8 | | Password last set date and time (pwdLastSet) <br> Contains a FILETIME
32 | 8 | | Account expires date and time (accountExpires) <br> Contains a FILETIME, where 0x7fffffffffffffff represents Never
40 | 8 | | Last password failure date and time (badPasswordTime) <br> Contains a FILETIME
48 | 4 | | Relative identifier (UserId) <br> The relative identifier (RID) corresponds to the the last authority of the SID
52 | 4 | | Primary group identifier (PrimaryGroupId)
56 | 4 | | User account control flags (UserAccountControl) <br> See section: [User account control flags](#user-account-control-flags)
60 | 2 | | Country code (countryCode) <br> See section: [Country code](#country-code)
62 | 2 | | Codepage (codePage)
64 | 2 | | Number of password failures (badPwdCount)
66 | 2 | | Number of logons (logonCount)
68 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
72 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
76 | 4 | | <mark style="background-color: yellow">**Unknown (checksum?)**</mark>

Extended data:

Offset | Size | Value | Description
--- | --- | --- | ---
80 | | |

Note that the relative identifier (RID) is sometimes referred to as user number
or user identifier.

#### User account control flags

The user account control flags (or USER_ACCOUNT Codes) are defined in subauth.h

Value | Identifier | Description
--- | --- | ---
0x00000001 | USER_ACCOUNT_DISABLED | Account disabled (inactive)
0x00000002 | USER_HOME_DIRECTORY_REQUIRED | Home directory required
0x00000004 | USER_PASSWORD_NOT_REQUIRED | User password not required
0x00000008 | USER_TEMP_DUPLICATE_ACCOUNT | Temporary duplicate account
0x00000010 | USER_NORMAL_ACCOUNT | Normal user account
0x00000020 | USER_MNS_LOGON_ACCOUNT | Majority Node Set (MNS) logon user account
0x00000040 | USER_INTERDOMAIN_TRUST_ACCOUNT | Interdomain trust account
0x00000080 | USER_WORKSTATION_TRUST_ACCOUNT | Workstation trust account
0x00000100 | USER_SERVER_TRUST_ACCOUNT | Server trust account <br> Object is a domain controller (DC)
0x00000200 | USER_DONT_EXPIRE_PASSWORD | User password does not expire
0x00000400 | USER_ACCOUNT_AUTO_LOCKED | Account auto locked
0x00000800 | USER_ENCRYPTED_TEXT_PASSWORD_ALLOWED | Encryped text password is allowed
0x00001000 | USER_SMARTCARD_REQUIRED | Smart Card required
0x00002000 | USER_TRUSTED_FOR_DELEGATION | Trusted for Delegation
0x00004000 | USER_NOT_DELEGATED | Not delegated
0x00008000 | USER_USE_DES_KEY_ONLY | Use DES key only
0x00010000 | USER_DONT_REQUIRE_PREAUTH | Preauth not required
0x00020000 | USER_PASSWORD_EXPIRED | Password Expired
0x00040000 | USER_TRUSTED_TO_AUTHENTICATE_FOR_DELEGATION | Used by Kerberos see MS-KILE
0x00080000 | USER_NO_AUTH_DATA_REQUIRED | Used by Kerberos see RFC4120
0x00100000 | USER_PARTIAL_SECRETS_ACCOUNT | Partial secrets account <br> Object is a read-only domain controller (RODC)
0x00200000 | USER_USE_AES_KEYS | Use AES keys

Note that these flags differ from ADS_USER_FLAG_ENUM. Mappings between the two
are defined in "MS-SAMR: userAccountControl Mapping Table".

Note that the samba project defines these as flags with the WBC_ACB prefix,
where WBC is short for winbind client.

#### Country code

<mark style="background-color: yellow">**Unknown. Is this suppose to be the country phone prefix?**</mark>

Value | Description
--- | ---
000 | System Default
001 | United States
002 | Canada (French)
003 | Latin America
031 | Netherlands
032 | Belgium
033 | France
034 | Spain
039 | Italy
041 | Switzerland
044 | United Kingdom
045 | Denmark
046 | Sweden
047 | Norway
049 | Germany
061 | Australia
081 | Japan
082 | Korea
086 | China (PRC)
088 | Taiwan
099 | Asia
351 | Portugal
358 | Finland
785 | Arabic
972 | Hebrew

### Account types

Value | Identifier | Description
--- | --- | ---
0x00000000 | SAM_DOMAIN_OBJECT | Represents a domain object
0x10000000 | SAM_GROUP_OBJECT | Represents a group object
0x10000001 | SAM_NON_SECURITY_GROUP_OBJECT | Represents a group object that is not used for authorization context generation
0x20000000 | SAM_ALIAS_OBJECT | Represents an alias object
0x20000001 | SAM_NON_SECURITY_ALIAS_OBJECT | Represents an alias object that is not used for authorization context generation
0x30000000 | SAM_USER_OBJECT | Represents a user object
0x30000001 | SAM_MACHINE_ACCOUNT | Represents a computer object
0x30000002 | SAM_TRUST_ACCOUNT | Represents a user object that is used for domain trusts
0x40000000 | SAM_APP_BASIC_GROUP | Represents an application-defined group
0x40000001 | SAM_APP_QUERY_GROUP | Represents an application-defined group whose members are determined by the results of a query

### Predefined RIDs

Value | Identifier | Description
--- | --- | ---
0x000001f4 | DOMAIN_USER_RID_ADMIN | User: Administrator
0x000001f5 | DOMAIN_USER_RID_GUEST | User: Guest
0x000001f6 | DOMAIN_USER_RID_KRBTGT | User: krbtgt (Key Distribution Center Service)
0x00000201 | DOMAIN_GROUP_RID_USERS | Group: Domain Users
0x00000203 | DOMAIN_GROUP_RID_COMPUTERS | Group: Domain Computers
0x00000204 | DOMAIN_GROUP_RID_CONTROLLERS | Group: Domain Controllers
0x00000220 | DOMAIN_ALIAS_RID_ADMINS | Group: Administrators
0x00000209 | DOMAIN_GROUP_RID_READONLY_CONTROLLERS | Group: Read-only Domain Controllers

## External Links

* [ACCOUNT_TYPE Values](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/e742be45-665d-4576-b872-0bc99d1e1fbe)
* [Built-in and Account Domains](https://docs.microsoft.com/en-us/windows/win32/secmgmt/built-in-and-account-domains)
* [Predefined RIDs](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/565a6584-3061-4ede-a531-f5c53826504b)
* [SAMPR_USER_ALL_INFORMATION](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/dc966b81-da27-4dae-a28c-ec16534f1cb9)
* [Security Account Manager (SAM)](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2003/cc756748(v=ws.10))
* [SysKey and the SAM](http://moyix.blogspot.com/2008/02/syskey-and-sam.html), by Brendan Dolan-Gavitt, February 21, 2008
* [USER_ACCOUNT Codes](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/b10cfda1-f24f-441b-8f43-80cb93e786ec)
* [userAccountControl Mapping Table](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/8a193181-a7a2-49df-a8b1-f689aaa6987c)
* [USER_ALL_INFORMATION structure](https://docs.microsoft.com/en-us/windows/win32/api/subauth/ns-subauth-user_all_information)
* [Well-known SIDs](https://docs.microsoft.com/en-us/windows/win32/secauthz/well-known-sids)

