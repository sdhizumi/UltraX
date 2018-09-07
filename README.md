# UltraX – MDX compiler for MXDRV2 

![](https://img.shields.io/badge/status-incomplete-red.svg)
![](https://img.shields.io/badge/version-v0.1-orange.svg)

UltraX is a compiler that creates MDX performance files for Sharp x68000 MXDRV2. It includes its own small library for MDX creation.

Also included is libPyFMT (a library for FM patch creation/manipulation) **[currently not available yet]**.


## Features

UltraX supports the following features:
- Native Python compiling to .MDX
- Native Python compiling to OKI ADPCM + .PDX (?)
- Supports all commands of the MXDRV v2.06+16/02EX specification
- Support for 1 channel ADPCM, PCM-4, PCM-8 and Mercury-Unit
- MML text file compiling
- DefleMask .dmf file (YM2151+SPCM mode) compiling


UltraX's core compiling system (pymdx) is written in a modular manner so that everybody could write their own compiler specialised in whatever way is desired. pymdx can do create, manipulate and export the following:
- MDX object
- Header object
- Tone definition object
- Track data (MDX commands), individually per channel

*See the documentation for an indepth explanation of all functions included in pymdx.* 


## Dependencies

UltraX relies on modules from Python's standard library (3.5), libPyFMT.
* Python standard library:
`ntpath, os, sys`

* libPyFMT:
`opmn`


## Goals

The following list presents the current ambitions of the project and if they are reached yet:

- [ ] Provide a MXDRV2 compiler on a modern operating system
- [ ] Provide a (built-in?) toolset with helping compose for MXDRV2
- [ ] Provide a way to convert DefleMask .dmf files to .MDX (+ .PDX)


## Changelog

. . .


## Contribution

Contributing to this project to improve it is always welcome. I highly recommend you to submit pull requests instead of maintaining your own fork. By doing this, it is less confusing for users.


## License

All included scripts, modules, etc. are licensed under the LGPL v3 license (see LICENSE file), unless stated otherwise in sourcecode files.

&nbsp;
