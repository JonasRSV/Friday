![logo](art/friday-logo.png)

Friday is a free and open-source no-wake-word voice assistant. Friday is currently under development

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
