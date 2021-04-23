import phue
import sys

if __name__ == "__main__":
    b = phue.Bridge(config_file_path="credentials.json")
    b.set_light(int(sys.argv[1]), "on", True, 5)
    b.set_light(int(sys.argv[1]), "bri", 200, 5)
