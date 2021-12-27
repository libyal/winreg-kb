# Local Security Authority (LSA)

Windows 2000 and later.

```
HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Lsa
```

## Boot key

The boot key can be determined as following.

Determine a 32-character string by combining the classnames of the following
subkeys:

* JD
* Skew1
* GBG
* Data

The string contains a base16 encoded 16-byte binary data that contains the
scrambled key data. To unscramble the key data:

```
scrambled_key = codecs.decode(class_name_string, 'hex')

key = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for index, scrambled_index in enumerate([
    8, 5, 4, 2, 11, 9, 13, 3, 0, 6, 1, 12, 14, 10, 15, 7]):
  key[index] = scrambled_key[scrambled_index]

key = codecs.encode(b''.join(key), 'hex')
```

## LSA key

The Local Security Authority (LSA) (or Syskey) is a 128-bit RC4 encryption key
used to protect credentials stored in the Windows Registry.

```
Key: HKEY_LOCAL_MACHINE\Security\Policy\PolSecretEncryptionKey
Default value
```

```
Windows XP

00000000  01 00 00 00 01 00 00 00  00 00 00 00              |..............?.|

RC4 encrypted data
00000000                                       fd d4 3f b3  |..............?.|
00000010  ee 4f cd 45 2d 02 e8 1e  f2 ac bd 4f fc 15 12 09  |.O.E-......O....|
00000020  0a b5 48 17 33 8f 42 79  8b 89 11 d8 ec 6e 1c ec  |..H.3.By.....n..|
00000030  38 5f 27 df 72 ca 57 96  8d 16 d9 37              |8_'.r.W....7..d.|

RC4 key material
00000030                                       c4 14 64 d1  |8_'.r.W....7..d.|
00000040  a8 47 7a d4 4b a3 62 d8  e7 2b ef 76              |.Gz.K.b..+.v|
```

```
md5 = MD5.new()
md5.update(boot_key)

iteration = 0
while iteration < 1000:
  md5.update(value_data[60:76])
  iteration += 1

rc4_key = md5.digest()

rc4 = ARC4.new(rc4_key)
decrypted_data = rc4.decrypt(value_data[12:60])

lsa_key = decrypted_data[16:32]
```

```
0x00000000  80 3a ce f0 5f 15 d3 11  b7 e6 00 80 5f 48 ca eb  .:.._......._H..

0x00000010  01 d6 5d f4 43 aa 0a 86  d9 42 d1 17 34 ce 66 7c  ..].C....B..4.f|
0x00000020  24 9a 83 44 c6 a7 57 30  44 dc 27 06 26 94 77 8a  $..D..W0D.'.&.w.
```

## NL$KM

```
Key: HKEY_LOCAL_MACHINE\Security\Policy\Secrets\NL$KM\CurrVal
Default value
```

```
Windows XP
00000000  48 00 00 00 48 00 00 20  9c c3 0c 00              |H...H.. ........|

DES encrypted data
00000000                                       c2 0d 08 10  |H...H.. ........|
00000010  9a 04 04 bf 14 8b c7 d0  0b e2 9c 40 52 a7 8e aa  |...........@R...|
00000020  01 49 25 70 71 dc a0 69  8e 6c 03 1c b7 db 19 5c  |.I%pq..i.l.....\|
00000030  8f f4 11 d1 8d 73 07 b0  6f 1a db 0b ee cb 69 7f  |.....s..o.....i.|
00000040  73 50 24 82 f8 e1 a6 27  97 a9 cc 04 8e e4 ca bb  |sP$....'........|
00000050  33 68 00 7c                                       |3h.||
```

```
decrypted data (_LSA_BLOB)

0x00000000  40 00 00 00 01 00 00 00  09 fe 44 48 1b 35 73 b7  @.........DH.5s.
0x00000010  3b 1d fc f7 48 9f c9 60  3b 60 7d cf 62 35 50 fd  ;...H..`;`}.b5P.
0x00000020  b5 d8 8f 21 75 ec 01 e9  85 25 96 6c 68 52 c9 30  ...!u....%.lhR.0
0x00000030  fb 1d b6 9d cd 8c 14 90  91 de f1 dd 5d d7 64 2a  ............].d*
0x00000040  ce 40 97 5a f1 59 71 20                           .@.Z.Yq 
```

```
Windows 7
00000000  00 00 00 01                                       |....a.!v.......N|

00000000              61 d8 21 76  d9 02 af de bd aa ba 4e  |....a.!v.......N|
00000010  f3 3f de 78 03 00 00 00  00 00 00 00 1a 7a 20 be  |.?.x.........z .|
00000020  73 10 0b 57 34 88 16 81  00 42 50 a1 8f 5e 78 46  |s..W4....BP..^xF|
00000030  bb f3 5e 61 9b 59 fa de  ff 14 7c c1 70 97 66 8e  |..^a.Y....|.p.f.|
00000040  c8 98 54 5c 8e 0e 13 7d  e7 ba 9a 98 8b cf a4 6f  |..T\...}.......o|
00000050  6d 84 5f 84 9c 9f d9 08  c3 5d 5c bd e9 1a 78 c6  |m._......]\...x.|
00000060  63 de 80 2d ec 3c 75 1f  1b e0 10 f5 24 1c 5d 41  |c..-.<u.....$.]A|
00000070  dd fa 85 7c 6e 20 cd 5e  a4 ac c0 53 7e c3 d6 ef  |...|n .^...S~...|
00000080  23 e2 2c b0 bd 74 52 19  cd a0 4e b2 00 00 00 00  |#.,..tR...N.....|
00000090  00 00 00 00 00 00 00 00  00 00 00 00              |............|
```

