#!/usr/bin/python3

import pylib.phue as phue
import pathlib


credentials = str(pathlib.Path(__file__).parent.absolute() / "pylib/credentials.json")


if __name__ == "__main__":
    b = phue.Bridge(config_file_path=credentials)

    ids = [light.light_id for light in b.lights]
    b.set_light(ids, "on", False, 5)
