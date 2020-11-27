
Rewrite of https://github.com/JonasRSV/friday-voice-assistant but in rust! :)

very much WIP

## Building 

We build with https://github.com/rust-embedded/cross to enable easy cross-compilation to different platforms. For this you need [docker](https://www.docker.com/) installed

### x86-unknown-linux-gnu

You probably don't have to use cross-compilation for this if you're on a linux machine, just enter friday and run 

```bash
cargo build --release
```

But if you want to use the docker builder:

```bash
NAME=friday-x86_64-unknown-linux-gnu

docker build -t "${NAME?}" . -f platforms/x86_64-unknown-linux-gnu.Dockerfile

cd friday && cross build --release --target x86_64-unknown-linux-gnu
```

### armv7-unknown-linux-gnueabinhf (Raspberry Pi 2, 3)

To build for your PI (2 and 3, this might also work for 4 but have not been tested).

```bash
NAME="friday-armv7-unknown-linux-gnueabinhf"

docker build -t "${NAME?}" . -f platforms/armv7-unknown-linux-gnueabinhf.Dockerfile

cd friday && cross build --release --target armv7-unknown-linux-gnueabihf && cd ..
```
