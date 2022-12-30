# Component object model (COM) class identifiers (CLSIDs)

The component object model (COM) class Identifier (CLSID) key can be found in:

```
HKEY_CLASSES_ROOT\CLSID\{%GUID%}
HKEY_CLASSES_ROOT\Wow6432Node\CLSID\{%GUID%}
```

Sub keys:

Name | Description
--- | ---
AuxUserType | Application's short display name and names
CLSID | Class identifiers
Control | ActiveX Control settings
Conversion | Convert dialog box format conversion settings
DataFormats | Data formats supported by an application
DefaultIcon | Default icon settings
Implemented Categories |
InprocServer | 16-bit in-process server settings
InProcServer32 | 32-bit (and 64-bit) in-process server settings
Insertable | Insert Object dialog box list box settings
Interface | Supported interface IDs (IIDs)
LocalServer32 | 32-bit local server application settings
MiscStatus | Settings how to create and display the object
PersistentHandler |
Verb | Application verbs

MSDN defines DefaultIcon as a REG_SZ value but in Windows XP it seems to be a
key where the icon resource identifier is stored in the default value of the
key.

Values:

Name | Data type | Description
--- | --- | ---
AppID | REG_SZ | Associated application identifier <br> Contains a string in the form: "{GUID}"
AutoConvertTo | REG_SZ | Automatic conversion class identifier
AutoTreatAs | REG_SZ | Automatically treat as (emulation) class identifier
InprocHandler | REG_SZ | 16-bit custom in-process handler
InprocHandler32 | REG_SZ | 32-bit custom in-process handler
LocalServer | REG_SZ| 16-bit local server application
ProgID | REG_SZ | Associated program identifier <br> Contains a string in the form: "Program.Component"
ToolBoxBitmap32 | REG_SZ | Toolbar or toolbox button bitmap <br> Contains a resource identifier
TreatAs | REG_SZ | Identifier of class that can emulate the current class
Version | REG_SZ | version number
VersionIndependentProgID | REG_SZ | Version independent associated program identifier

## Type libraries key

The type libraries (typelib or tlb) key can be found in:

```
HKEY_CLASSES_ROOT\TypeLib\{%GUID%}
HKEY_CLASSES_ROOT\Wow6432Node\TypeLib\{%GUID%}
```

Sub keys:

Name | Description
--- | ---
%GUID% | Type library identifier

## Type library identifier subkey

Sub keys:

Name | Description
--- | ---
%VERSION% | Type library version in the format: "major.minor"

Values:

Name | Data type | Description
--- | --- | ---
(Default) | REG_SZ | Type library description

### Type library version subkey

Sub keys:

Name | Description
--- | ---
%LCID% | Locale identifier such as: "409", where "0" is the system default language (LANG_SYSTEM_DEFAULT).
FLAGS |
HELPDIR |

TODO: Determine what MSDN means with the LCID may have a neutral sublanguage
ID. Is 0 the neutral sublanguage ID?

#### Type library locale subkey

Sub keys:

Name | Description
--- | ---
%PLATFORM% | Platform identifier such as: "win32"

##### Type library platform subkey

Values:

Name | Data type | Description
--- | --- | ---
(Default) | REG_SZ | Path to the type library file. <br> This can be a stand-alone .tlb file or the "typelib" resource inside a PE/COFF file.

#### Type library help directory subkey

Values:

Name | Data type | Description
--- | --- | ---
(Default) | REG_SZ | Path of the directory where the Help file for type library is located

## External Links

* [CLSID Key](https://learn.microsoft.com/en-us/windows/win32/com/clsid-key-hklm)
* [ProxyStubClsid](https://learn.microsoft.com/en-us/windows/win32/com/proxystubclsid)
* [Registering a Type Library](https://learn.microsoft.com/en-us/previous-versions/windows/desktop/automat/registering-a-type-library)

