import phue
import sys
import math


def rgb_to_xy(red, green, blue):
    print(red, green, blue)
    if red > 0.04045:
        red = math.pow((red + 0.055) / (1.0 + 0.055), 2.4)
    else:
        red = red / 12.92

    if green > 0.04045:
        green = math.pow((green + 0.055) / (1.0 + 0.055), 2.4)
    else:
        green = green / 12.92

    if blue > 0.04045:
        blue = math.pow((blue + 0.055) / (1.0 + 0.055), 2.4)
    else:
        blue = blue / 12.92

    X = red * 0.664511 + green * 0.154324 + blue * 0.162028
    Y = red * 0.283881 + green * 0.668433 + blue * 0.047685
    Z = red * 0.000088 + green * 0.072310 + blue * 0.986039

    x = X / (X + Y + Z)
    y = Y / (X + Y + Z)
    return [x, y]


colors = {
    "red": [255, 0, 0],
    "green": [0, 255, 0],
    "blue": [0, 0, 255]
}

if __name__ == "__main__":
    b = phue.Bridge(config_file_path="credentials.json")
    print(b.get_api())

    b.set_light(int(sys.argv[1]), parameter={"on": True, "bri": 200, "xy": rgb_to_xy(*colors[sys.argv[2]])},
                transitiontime=5)
