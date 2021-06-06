# Cached Credentials

```
HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Winlogon
```

Values:

Value | Data type | Description
--- | --- | ---
CachedLogonsCount | REG_SZ | Number of cached log-ons. <br/> According to MSDN the value must be in the range "0" - "50"

## Credentials cache

```
HKEY_LOCAL_MACHINE\Security\Cache
```

Values:

Name | Description
--- | ---
NL$Control |
NL$%NUMBER% | Cached credential

Where %NUMBER% contains the number of the cached credential.

### NL$Control value

```
00000000  04 00 01 00 0a 00 00 00                           |........|
```

### NL$%NUMBER% value

Offset | Size | Value | Description
--- | --- | --- | ---
<td colspan=4> _Metadata_
0 | 2 | | Username string size
2 | 2 | | Hostname string size
4 | 2 | | <mark style="background-color: yellow">**Unknown (username string size)**</mark>
6 | 2 | | <mark style="background-color: yellow">**Unknown (Full name string size)**</mark>
8 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
12 | 2 | | <mark style="background-color: yellow">**Unknown (Profile path string size)**</mark>
14 | 2 | | <mark style="background-color: yellow">**Unknown (Profile mount drive letter string size)**</mark>
16 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
20 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
24 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
28 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
30 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
32 | 8 | | <mark style="background-color: yellow">**Unknown (date and time)**</mark> <br/> Contains a FILETIME timestamp
40 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
42 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
44 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
48 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
52 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
56 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
60 | 2 | | Hostname with domain string size
62 | 2 | | <mark style="background-color: yellow">**Unknown**</mark>
<td colspan=4> _Data_
64 | 16 | | <mark style="background-color: yellow">**Unknown (CH)**</mark>
80 | 16 | | <mark style="background-color: yellow">**Unknown (T)**</mark>
96 | ... | | Encrypted data

```
metadata
* username size
* domain size
* Length of the full domain name

0x00000000  0e 00 14 00 0e 00 1c 00  00 00 00 00 38 00 04 00  ............8...
0x00000010  53 04 00 00 01 02 00 00  02 00 00 00 14 00 18 00  S...............

0x00000020  72 0f 92 b3 b1 f8 cc 01                           r...............
FILETIME

0x00000020                           04 00 01 00 01 00 00 00  r...............
0x00000030  01 00 00 00 20 00 00 00  10 00 00 00 20 00 00 00  .... ....... ...

CH: random 16 byte key that is used to generate the decryption key for the encrypted data
0x00000040  e6 ad 1f 22 b9 d1 d3 48  22 f6 d6 61 33 d7 32 74  ..."...H"..a3.2t

T
0x00000050  29 4c 83 1b af bc ca c9  fc 27 9c be 1e 44 2b 69  )L.......'...D+i

Encrypted data
0x00000060  52 46 67 5f f6 85 b0 0f  7a a3 69 03 cc 72 4b 8b  RFg_....z.i..rK.
0x00000070  8b 51 e9 9c 4a 65 92 2d  19 7d 6f 94 d2 81 93 0d  .Q..Je.-.}o.....
0x00000080  f2 9e 7d 2e 11 17 46 a0  31 ac 2c 65 49 89 c2 c0  ..}...F.1.,eI...
0x00000090  92 7a 63 6c ca b2 74 ba  5f 73 c0 d3 6c 0c 58 51  .zcl..t._s..l.XQ
0x000000a0  46 e9 45 48 9b ce 86 a1  68 ae f7 12 f8 d2 c7 7e  F.EH....h......~
0x000000b0  4d 39 a9 bd d4 ad fc e8  b0 b1 94 36 c5 4d 1f 3b  M9.........6.M.;
0x000000c0  3c ce b8 dc a9 50 41 54  f4 5a 31 61 57 66 66 7a  <....PAT.Z1aWffz
0x000000d0  0d 54 9a c0 7e d4 1a a8  e6 af 83 fb cd 61 a1 fe  .T..~........a..
0x000000e0  85 31 ce c9 24 fa f3 a5  7e 71 c9 a4 81 11 e3 b7  .1..$...~q......
0x000000f0  7c ce fb 38 b0 81 b9 75  cc 78 7e 66 9c 7b 4d a7  |..8...u.x~f.{M.
0x00000100  7d 6e 55 d6 8d 22 2d e9  8d 48 0c 22 f1 bc 6b 58  }nU.."-..H."..kX
0x00000110  17 84 db 5b ba 91 8a 39  70 a1 d8 b5 16 df 99 cf  ...[...9p.......
0x00000120  ea f1 af dc 75 27 ea 83  22 ff 8a 5e 63 b2 a9 f9  ....u'.."..^c...
0x00000130  b4 05 47 26 b8 e7 e4 b7  06 bc d9 4b 0f 20 92 25  ..G&.......K. .%
0x00000140  07 7a a5 6b 4e 54 4a 19  19 51 bf 5f c2 09 8b 5e  .z.kNTJ..Q._...^
0x00000150  f1 a3 be aa 1f c3 66 c3  cd 09 7b 85 45 02 0d 28  ......f...{.E..(
0x00000160  02 a5 f8 8a f2 b1 52 a3  a3 dc a4 c7 ed f5 ca 6c  ......R........l
0x00000170  13 3c e5 18 3d fe b3 fc  28 3f be 9b 62 d0 1a 5a  .<..=...(?..b..Z
0x00000180  90 ce e2 a6 c2 aa 2d 40  78 d8 cc db a4 a7 44 e8  ......-@x.....D.
0x00000190  0d ff c8 08 49 19 5b 21  67 f2 62 be 7b f2 be d3  ....I.[!g.b.{...
0x000001a0  37 18 53 33 61 3e 21 7a  e6 08 e3 f2 d5 1c 81 ce  7.S3a>!z........
0x000001b0  9a 45 71 85 bf a6 e9 fd  ea 7e b7 2f 01 0d 7d c7  .Eq......~./..}.
0x000001c0  46 9f e5 73                                       F..s
```

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 16 | | <mark style="background-color: yellow">**Unknown (password hash)**</mark>
16 | 16 | | <mark style="background-color: yellow">**Unknown**</mark>
32 | 8 | | <mark style="background-color: yellow">**Unknown**</mark>
40 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
44 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
48 | 8 | | <mark style="background-color: yellow">**Unknown**</mark>
56 | 16 | | <mark style="background-color: yellow">**Unknown**</mark>
72 | ... | | Username string
... | ... | | 32-bit alignment padding
... | ... | | Hostname string
... | ... | | 32-bit alignment padding
... | ... | | Hostname and domain string
... | ... | | 32-bit alignment padding
... | ... | | Profile path string
... | ... | | 32-bit alignment padding
... | ... | | Profile mount drive letter string
... | ... | | 32-bit alignment padding

```
Decrypted data:
0x00000000  6e 37 5e e6 a7 99 6c 5c  55 85 74 67 09 af a0 65  n7^...l\U.tg...e
0x00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
0x00000020  01 00 00 00 00 00 00 00  c4 01 00 00 02 00 00 00  ................
0x00000030  14 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  ................
0x00000040  00 00 00 00 00 00 00 00                           ........t.d.u.n.

Sizes from metadata
0e 00 14 00 0e 00 1c 00

0x00000040                           74 00 64 00 75 00 6e 00  ........t.d.u.n.
0x00000050  67 00 61 00 6e 00                                 g.a.n...S.H.I.E.

0x00000050                    00 00                           g.a.n...S.H.I.E.

0x00000050                           53 00 48 00 49 00 45 00  g.a.n...S.H.I.E.
0x00000060  4c 00 44 00 42 00 41 00  53 00 45 00              L.D.B.A.S.E.S.H.

0x00000060                                       53 00 48 00  L.D.B.A.S.E.S.H.
0x00000070  49 00 45 00 4c 00 44 00  42 00 41 00 53 00 45 00  I.E.L.D.B.A.S.E.

0x00000080  2e 00 4c 00 4f 00 43 00  41 00 4c 00              ..L.O.C.A.L.t.d.

0x00000080                                       74 00 64 00  ..L.O.C.A.L.t.d.
0x00000090  75 00 6e 00 67 00 61 00  6e 00 00 00              u.n.g.a.n...T.i.

0x00000090                                       54 00 69 00  u.n.g.a.n...T.i.
0x000000a0  6d 00 6f 00 74 00 68 00  79 00 20 00 44 00 75 00  m.o.t.h.y. .D.u.
0x000000b0  6e 00 67 00 61 00 6e 00                           n.g.a.n.\.\.c.o.

0x000000b0                           5c 00 5c 00 63 00 6f 00  n.g.a.n.\.\.c.o.
0x000000c0  6e 00 74 00 72 00 6f 00  6c 00 6c 00 65 00 72 00  n.t.r.o.l.l.e.r.
0x000000d0  5c 00 68 00 6f 00 6d 00  65 00 5c 00 25 00 75 00  \.h.o.m.e.\.%.u.
0x000000e0  73 00 65 00 72 00 6e 00  61 00 6d 00 65 00 25 00  s.e.r.n.a.m.e.%.

0x000000f0  48 00 3a 00 01 02 00 00  07 00 00 00 07 02 00 00  H.:.............
0x00000100  07 00 00 00 53 00 48 00  49 00 45 00 4c 00 44 00  ....S.H.I.E.L.D.
0x00000110  42 00 41 00 53 00 45 00  07 00 00 20 01 05 00 00  B.A.S.E.... ....
0x00000120  00 00 00 05 15 00 00 00  97 2a 67 79 a0 54 4a b6  .........*gy.TJ.
0x00000130  19 87 28 7e 3c 02 00 00  01 04 00 00 00 00 00 05  ..(~<...........
0x00000140  15 00 00 00 97 2a 67 79  a0 54 4a b6 19 87 28 7e  .....*gy.TJ...(~
0x00000150  43 00 4f 00 4e 00 54 00  52 00 4f 00 4c 00 4c 00  C.O.N.T.R.O.L.L.
0x00000160  45 00 52 00                                       E.R.
```

NL$7

```
00000000  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000010  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  04 00 01 00 00 00 00 00  |................|
00000030  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000040  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000050  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000060  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000070  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000080  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
00000090  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
000000a0  00 00 00 00 00 00 00 00                           |........|
```

## External Links

* [Cached domain logon information](https://docs.microsoft.com/en-US/troubleshoot/windows-server/user-profiles-and-logon/cached-domain-logon-information)

