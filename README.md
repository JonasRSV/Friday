![logo](art/friday-logo.png)

Friday is a free and open-source no-wake-word voice assistant. Friday and its [website](https://markusaj13.github.io/Monday/?page=home&lang=english) is currently under development

Contents
- [Roadmap](#roadmap)
- [Contribute](#contribute)
- [Installation](#Installation)



## Roadmap

* [x] Implement v1 Keyword spotting Engine
* [x] Implement Philips Hue vendor to control lights
* [ ] Add user manual and docs
* [ ] Implement v2 Keyword spotting Engine
* [ ] Add easy-to-use interfaces

## Contribute

Assistant specific code is under friday/ - Models are found under mm/ (model making)

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
