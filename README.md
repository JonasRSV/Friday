![logo](art/friday-logo.png)

Friday is a free and open-source no-wake-word voice assistant. Friday is currently under development

Contents
- [Contribute](#contribute)
- [Installation](#Installation)

## Features

* [x] Philips Hue 
* [x] GUI
* [ ] Custom Scripts

## Contribute

- on-device assistant specific code is under friday/ 
- model making is found under mm/ 
- art (such as banner|logo|..) is found under art/
- websites are under web/

## Installation 

Cross compilation have been tested for

* [x] x86 Linux
* [x] Raspberry Pi 3
* [ ] Raspberry Pi 4
* [ ] Windows
* [ ] Mac

Use the build script to compile, see: 

```bash
./build -h
```

For example to build for x86_64 linux

```bash
./build -li
```
