# Friday on Linux X86
---

- [Prerequisites](#prerequisites)
- [Releases](#releases)
- [Build](#build)

## Prerequisites

Friday uses libtensorflow, make sure you have it installed in your library by running


```bash
ldconfig -p | grep libtensorflow
```


If this command is empty, unzip the library file from platforms.Resources/libtensorflow-unknown-linux_x86.zip and copy the contents to /usr/local/lib, then run

```bash
sudo ldconfig
```



## Releases

Precompiled Linux X86 are not available yet, to try it out you'll have to build it yourself

## Build

Clone this repository 

```bash
git clone https://github.com/JonasRSV/Friday
```

Navigate into the root

```bash
cd Friday
```


Use the build script to build the Friday binary, the script will use [cross](https://github.com/rust-embedded/cross) to compile in a docker container.


```bash
./build -li
```

It is likely that you are missing a lot of dependencies, the build script will give you instructions on what is missing and where to install it from. Once the binary is built you should see it in

```bash
ls $PWD/bin
```

To create a release: a bundle with files for GUI, model, configurations and the binary; run the release script

```bash
./release -li
```

This should create a directory under releases/release-linux that contains all files necessary to launch the assistant.  To launch, navigate into the release and run

```bash
FRIDAY_CONFIG=. FRIDAY_GUI=nightout ./friday-x86_64-unknown-linux-gnu
```

Now, there are many things you might want to configure, such as what microphone the assistant should use and some hyperparameters for voice activity detection. See all 
configuration options in the [configs](CONFIG.md) guide.


