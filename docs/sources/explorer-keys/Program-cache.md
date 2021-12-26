# Program cache

The Windows explorer ProgramsCache Registry values can be stored in
the following Windows Registry keys.

* Explorer\\StartPage key
* Explorer\\StartPage2 key

## Explorer\\StartPage key

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\StartPage
```

Seen in Windows XP, 2003 and Vista.

Values:

Name | Data type | Description
--- | --- | ---
ProgramsCache | REG_BINARY | All the started the programs. <br> <mark style="background-color: yellow">**Contains a Jump list?**</mark>

## Explorer\\StartPage2 key

```
HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\StartPage2
```

Seen in Windows 7.

Values:

Name | Data type | Description
--- | --- | ---
ProgramsCache | REG_BINARY | All the started the programs. <br> <mark style="background-color: yellow">**Contains a Jump list?**</mark>
ProgramsCacheSMP | REG_BINARY | The applications pinned to the Start Menu. <br> Contains a Jump list.
ProgramsCacheTBP | REG_BINARY | The applications pinned to the Taskband. <br> Contains a Jump list.

Note that the format of the ProgramsCache value data slightly differs from that
of the ProgramsCacheSMP and ProgramsCacheTBP value data.

## ProgramsCache value data format

ProgramsCacheSMP - Empty list

```
00000000  01 00 00 00                                       |.........|
00000000              00 00 00 00                           |.........|
00000000                           02                       |.........|
```

ProgramsCacheTBP

```
0x00000000  01 00 00 00 0b 00 00 00  01 aa 02 00 00           ................

0x00000000  01 00 00 00 07 00 00 00  01 0e 03 00 00           ................

00000000  01 00 00 00                                       |................|
number of entries?
00000000              0e 00 00 00                           |................|
start of entry marker?
00000000                           01                       |................|
relative offset to next entry?
00000000                              f2 02 00 00           |................|
00000000                                          14 00 1f  |................|

shell item list
00000010  80 c8 27 34 1f 10 5c 10  42 aa 03 2e e4 52 87 d6  |..'4..\.B....R..|
...
000002f0  00 78 00 65 00 00 00 00  00 00 00 1c 00           |.x.e............|
end of list?
000002f0                                          00 00     |.x.e............|
start of entry marker?
000002f0                                                01  |.x.e............|
00000300  3c 02 00 00                                       |<........'4..\.B|

shell item list
00000300              14 00 1f 80  c8 27 34 1f 10 5c 10 42  |<........'4..\.B|
...
00000bb0  4f 00 4b 00 2e 00 45 00  58 00 45 00 00 00 00 00  |O.K...E.X.E.....|
00000bc0  00 00 1c 00                                       |.......|
end of list?
00000bc0              00 00                                 |.......|
00000bc0                    02                              |.......|
```

StartPage2\ProgramsCache

```
Window 7
00000000  13 00 00 00 c3 53 5b 62  48 ab c1 4e ba 1f a1 ef  |.....S[bH..N....|
00000010  41 46 fc 19 00 80 00 00  00                       |AF.......~.1....|

shell item list?
00000010                              7e 00 31 00 00 00 00  |AF.......~.1....|
00000020  00 6a 3d 6c 3e 11 00 50  72 6f 67 72 61 6d 73 00  |.j=l>..Programs.|
00000030  00 66 00 08 00 04 00 ef  be 6a 3d 53 3e 6a 3d 6c  |.f.......j=S>j=l|
00000040  3e 2a 00 00 00 c1 e2 00  00 00 00 01 00 00 00 00  |>*..............|
00000050  00 00 00 00 00 3c 00 00  00 00 00 50 00 72 00 6f  |.....<.....P.r.o|
00000060  00 67 00 72 00 61 00 6d  00 73 00 00 00 40 00 73  |.g.r.a.m.s...@.s|
00000070  00 68 00 65 00 6c 00 6c  00 33 00 32 00 2e 00 64  |.h.e.l.l.3.2...d|
00000080  00 6c 00 6c 00 2c 00 2d  00 32 00 31 00 37 00 38  |.l.l.,.-.2.1.7.8|
00000090  00 32 00 00 00 18 00 00  00                       |.2........<...:.|

00000090                              01 3c 02 00 00        |.2........<...:.|

shell item list?
00000090                                             3a 02  |.2........<...:.|
000000a0  32 00 85 05 00 00 30 3f  97 a9 20 00 49 4e 54 45  |2.....0?.. .INTE|
000000b0  52 4e 7e 31 2e 4c 4e 4b  00 00 b8 00 08 00 04 00  |RN~1.LNK........|
000000c0  ef be 6a 3d 6c 3e 6a 3d  6c 3e 2a 00 00 00 b8 e3  |..j=l>j=l>*.....|

...
00012e80  00 00 00 00 00 00 1c 00  00 00 02                 |...........|


0x00019890  6d 00 2e 00 65 00 78 00  65 00 00 00 00 00 00 00  m...e.x.e.......
0x000198a0  20 00 00 00                                        ......9....O.'H

TODO: edge case or remnant data?
0x000198a0              02 ab 95 39  9e 9c 1f 13 4f b8 27 48   ......9....O.'H
0x000198b0  b2 4b 6c 71 74 00                                 .Klqt.T...R.1...

0x000198b0                    54 00  00 00 52 00 31 00 00 00  .Klqt.T...R.1...
0x000198c0  00 00 0c 3d a4 33 11 00  54 61 73 6b 42 61 72 00  ...=.3..TaskBar.
0x000198d0  3c 00 08 00 04 00 ef be  0c 3d a4 33 0c 3d a4 33  <........=.3.=.3
0x000198e0  2a 00 00 00 69 ee 00 00  00 00 04 00 00 00 00 00  *...i...........
```

StartPage\ProgramsCache

```
Windows XP and 2003
00000000  09 00 00 00 0b 00                                 |......V...T.1...|

data size
00000000                    56 00  00 00                    |......V...T.1...|
shell item list
00000000                                 54 00 31 00 00 00  |......V...T.1...|
00000010  00 00 04 3b a3 79 11 00  50 72 6f 67 72 61 6d 73  |...;.y..Programs|
00000020  00 00 3c 00 03 00 04 00  ef be 04 3b 8c 79 04 3b  |..<........;.y.;|
00000030  a3 79 14 00 26 00 50 00  72 00 6f 00 67 00 72 00  |.y..&.P.r.o.g.r.|
00000040  61 00 6d 00 73 00 00 00  40 73 68 65 6c 6c 33 32  |a.m.s...@shell32|
00000050  2e 64 6c 6c 2c 2d 32 31  37 38 32 00 18 00 00 00  |.dll,-21782.....|

00000060  01 d4 00 00 00                                    |.......2.#....;.|

00000060                 d2 00 32  00 23 03 00 00 04 3b a3  |.......2.#....;.|
00000070  79 20 00 49 4e 54 45 52  4e 7e 31 2e 4c 4e 4b 00  |y .INTERN~1.LNK.|
00000080  00 42 00 03 00 04 00 ef  be 04 3b a3 79 04 3b a3  |.B........;.y.;.|
...
0x000003e0  1c 00 00 00                                       .........T.1....
sentinel of 0x00 seen before shell item list with more than one shell item?
0x000003e0              00 b0 00 00  00                       .........T.1....
shell item list
0x000003e0                              54 00 31 00 00 00 00  .........T.1....
0x000003f0  00 04 3b a3 79 11 00 50  72 6f 67 72 61 6d 73 00  ..;.y..Programs.
...
0x00001020  00 00 00 00 00 1c 00 00  00                       ................
unknown data 9 bytes (0x02 end marker?)
0x00001020                              02 16 00 02 00 00 00  ................
0x00001030  00 00                                             .........2.....:
data size
0x00001030        01 ea 00 00 00                              .........2.....:
shell item list
0x00001030                       e8  00 32 00 1b 06 00 00 3a  .........2.....:
...
0x00004a40  00 65 00 78 00 65 00 00  00 00 00 1c 00 00 00     .e.x.e..........
unknown data 11 bytes
0x00004a40                                                02  .e.x.e..........
0x00004a50  10 02 19 00 02 00 00 00  00 00                    ................
0x00004a50                                 01 ca 00 00 00     ................
0x00004a50                                                c8  ................
0x00004a60  00 32 00 42 06 00 00 04  3b 12 7a 20 00 4d 4f 5a  .2.B....;.z .MOZ
...
00004b10  00 65 00 66 00 6f 00 78  00 2e 00 65 00 78 00 65  |.e.f.o.x...e.x.e|
00004b20  00 00 00 00 00 1c 00 00  00                       |..........|
00004b20                              02                    |..........|
```

```
Windows Vista (c3535b62-48ab-c14e-ba1f-a1ef4146fc19 FOLDERID_StartMenu)

0x00000000  0c 00 00 00 c3 53 5b 62  48 ab c1 4e ba 1f a1 ef  .....S[bH..N....
0x00000010  41 46 fc 19                                       AF...|...z.1....
0x00000010              00 7c 00 00  00                       AF...|...z.1....
...
0x00009fe0  72 00 33 00 32 00 2e 00  65 00 78 00 65 00 00 00  r.3.2...e.x.e...
0x00009ff0  00 00 00 00 1c 00 00 00                           .........a.O..M.

TODO: edge case or remnant data?
0x00009ff0                           02 61 ae 4f 05 d8 4d 87  .........a.O..M.
0x0000a000  47 80 b6 09 02 20 c4 b7  00 02                    G.... ....
```

Value data header Windows XP and 2003.

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0x00000009 | Format version
4 | 2 | 0x000b | <mark style="background-color: yellow">**Unknown**</mark>

Value data header Windows Vista.

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0x0000000c | Format version
4 | 16 | | Known folder identifier <br> Contains a GUID <br> c3535b62-48ab-c14e-ba1f-a1ef4146fc19 (FOLDERID_StartMenu)
20 | 1 | | <mark style="background-color: yellow">**Unknown (sentinel?)**</mark>

ProgramsCache value data header Windows 7 and 2008.

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0x00000013 | Format version
4 | 16 | | Known folder identifier <br> Contains a GUID <br> c3535b62-48ab-c14e-ba1f-a1ef4146fc19 (FOLDERID_StartMenu)
20 | 1 | | <mark style="background-color: yellow">**Unknown (sentinel?)**</mark>

ProgramsCacheSMP and ProgramsCacheTBP value data header Windows 7 and 2008.

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | 0x00000001 | Format version
4 | 4 | | <mark style="background-color: yellow">**Unknown**</mark>
5 | 1 | | <mark style="background-color: yellow">**Unknown (sentinel?)**</mark>

Value data entry.

Offset | Size | Value | Description
--- | --- | --- | ---
0 | 4 | | Entry data size
4 | ... | | Entry data <br> Contains a shell item list
... | 1 | | <mark style="background-color: yellow">**Unknown (sentinel?)**</mark> <br> <mark style="background-color: yellow">**Seen 0x00, 0x01, 0x02 (end marker?)**</mark>

<mark style="background-color: yellow">**if sentinel is 0x02 and there is more data then look
for 0x00 which should be followed by 02 00 00 00 00 00 01**</mark>

