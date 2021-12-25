# Windows Error Reporting (WER) keys

## Windows Error Reporting (WER) system key

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\Windows Error Reporting
```

Sub keys:

Name | Description
--- | ---
Assert Filtering Policy |
BrokerUp |
Consent |
Debug |
Hangs |
HeapControlledList |
LocalDumps |
RuntimeExceptionHelperModules |
WMR |

Values:

Name | Data type | Description
--- | --- | ---
BypassDataThrottling | REG_DWORD | Bypass WER client data throttling
ConfigureArchive | REG_DWORD | Archive only the parameters or all data
EnableZip | REG_DWORD |
ErrorPort | REG_SZ |
MachineID | |
MaxQueueSizePercentage | |
PurgeThreshholdValueInKB | |
ServiceTimeout | REG_DWORD |

### BypassDataThrottling value

0 - Disable data bypass throttling
1 - Enable data bypass throttling

### ConfigureArchive value

1 - Parameters only (default on Windows 7)
2 - All data (default on Windows Vista)

### Consent sub key

Values:

Name | Data type | Description
--- | --- | ---
DefaultConsent | REG_DWORD | The default consent choice
DefaultOverrideBehavior | REG_DWORD | The default consent overrides the vertical consent
NewUserDefaultConsent | REG_DWORD |

#### DefaultConsent value

1 - Always ask (default)
2 - Parameters only
3 - Parameters and safe data
4 - All data

#### DefaultOverrideBehavior value

0 - Vertical consent will override the default consent (default)
1 - Default consent will override the application-specific consent|

### Debug sub key

Sub keys:

Name | Description
--- | ---
UIHandles |

Values:

Name | Data type | Description
--- | --- | ---
StoreLocation | REG_SZ | Location of last report?

#### UI handles sub key

Values:

Name | Data type | Description
--- | --- | ---
CheckingForSolutionDialog | |
CloseDialog | |
FirstLevelConsentDialog | |
RecoveryDialog | |
RestartDialog | |

### Hangs sub key

Values:

Name | Data type | Description
--- | --- | ---
NHRTimes | |

### Local dumps sub key

Per-application setting can be define by an application-specific key under:

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\Windows Error Reporting\LocalDumps
```

For example an application-key for MyApplication.exe

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\Windows Error Reporting\LocalDumps\MyApplication.exe
```

Values:

Name | Data type | Description
--- | --- | ---
DumpCount | REG_DWORD | The maximum number of dump files in the folder. Older dump files are overwritten if the maximum has been reached. <br> By default: 10
DumpFolder | REG_EXPAND_SZ | The path where the dump files are to be stored. <br> By default: %LOCALAPPDATA%\CrashDumps
DumpType | REG_DWORD | The dump type <br> By default: 1 (Mini dump)
CustomDumpFlags | REG_DWORD | Custom dump flag when dump type is 0 (Custom dump).

#### DumpType value

Value | Description
--- | ---
0 | Custom dump
1 | Mini dump (default)
2 | Full dump

#### CustomDumpFlags value

The CustomDumpFlags value contains a bitwise combination of the MINIDUMP_TYPE
enumeration values.

## Windows Error Reporting (WER) user key

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\Windows Error Reporting
```

Sub keys:

Name | Description
--- | ---
Consent |
Hangs |

Values:

Name | Data type | Description
--- | --- | ---
AutoApproveOSDumps | REG_DWORD |
Disabled | REG_DWORD |
DisableArchive | REG_DWORD |
DisableQueue | REG_DWORD |
DontSendAdditionalData | REG_DWORD |
DontShowUI | REG_DWORD |
ForceQueue | REG_DWORD |
LastCrashSelfReportTime | |
LastQueuePesterTime | REG_QWORD_LITTLE_ENDIAN |
LastResponsePesterTime | |
LoggingDisabled | REG_DWORD |
MaxArchiveCount | REG_DWORD |
MaxQueueCount | REG_DWORD |
MaxQueueSize | REG_DWORD |

## Notes

### Kernel faults sub key

Sub keys:

Name | Description
--- | ---
Queue |

#### Queue sub key

Values:

Name | Data type | Description
--- | --- | ---
%FILENAME% | | Creation time of the minidump? <br> Contains a FILETIME

```
C:\\Windows\\Minidump\\MMDDYY-#-01.dmp
```

### Other

C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\WER

Sub directories:

Name | Description
--- | ---
ERC |
ReportArchive |
ReportQueue |

## External Links

* [MSDN: Collecting User-Mode Dumps](http://msdn.microsoft.com/en-us/library/windows/desktop/bb787181(v=vs.85).aspx)
* [MSDN: MINIDUMP_TYPE enumeration](http://msdn.microsoft.com/en-us/library/windows/desktop/ms680519(v=vs.85).aspx)
* [MSDN: WER Settings](http://msdn.microsoft.com/en-us/library/windows/desktop/bb513638(v=vs.85).aspx)
