# Linux X86


Prerequisites:

1. Make sure you are at the repository root.


Start by building the binary

```bash
./build -li
```

The script will tell you if you're missing any dependecies, and also suggest fixes.  If all went well you should now have the binary file **bin/friday-x86_64-unknown-linux-gnu**


Continue by creating a linux release

```bash
./release -li
```

All files you need should now be available under releases/release-linux that directory can be copied to wherever you want to run the assistant.

to launch the assistant, navigate into the release and run

```bash
FRIDAY_CONFIG=. FRIDAY_GUI=nightout ./friday-x86_64-unknown-linux-gnu
```

Now there are a lot of configurations - for details on them see [configs](CONFIG.md)


In case you could not start the assistant, please make sure you have libtensorflow in your library path. You can do this by running

```bash
ldconfig -p | grep libtensorflow
```

If this command is empty, unzip the library file from platforms.Resources and copy the contents to /usr/local/lib, then run

```bash
sudo ldconfig
```

and try again... if it still does not work, please open an issue.
