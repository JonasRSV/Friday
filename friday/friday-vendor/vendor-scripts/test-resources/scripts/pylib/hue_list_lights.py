import phue

if __name__ == "__main__":
    b = phue.Bridge(config_file_path="credentials.json")

    for light in b.lights:
        print(f"name {light.name} - id {light.light_id} - on {light.on}")
