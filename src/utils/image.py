import requests
import discord

from PIL import Image
from io import BytesIO
from numpy import array

def rgb_to_str(rgb: list) -> str:
    return f"{rgb[0]} {rgb[1]} {rgb[2]}"

def str_to_rgb(rgb_str: str) -> list:
    return [int(val) for val in rgb_str.split(" ")]

def rgb_to_hsv(rgb: list) -> list:
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]

    minn = min(r, g, b)
    maxx = max(r, g, b)

    hue = 0
    sat = 0 if maxx == 0 else 1 - minn / maxx
    val = maxx / 255

    if (maxx - minn != 0):
        match str(maxx):
            case str(r): hue = (g - b) / (maxx - minn)
            case str(g): hue = (b - r) / (maxx - minn) + 2
            case str(b): hue = (r - g) / (maxx - minn) + 4
        
        hue = hue * 60
        hue %= 360

    return [
        round(hue + 360 if hue < 0 else hue),
        round(sat * 100),
        round(val * 100),
    ]

def is_near_rgb(one: list, two: list, near = 12) -> bool | int:
    delta_r = one[0] - two[0]
    delta_g = one[1] - two[1]
    delta_b = one[2] - two[2]

    if (delta_r <= near and delta_r >= -near and
        delta_g <= near and delta_g >= -near and
        delta_b <= near and delta_b >= -near):
            return True, abs(delta_r) + abs(delta_g) + abs(delta_b)

    return False, 999

def is_vibrant(hsv: list) -> bool:
    sat = hsv[1]
    val = hsv[2]

    if (#sat >= 85 and val >= 50 or
        sat >= 55 and val >= 65 or
        sat >= 45 and val >= 75):
            return True

    return False

async def get_prominent_color(url: str) -> discord.Color:
    res = requests.get(url)
    img = Image.open(BytesIO(res.content))

    w, h = img.size

    pixels = list(img.getdata())

    # turn to 2D array
    pixels = array(list(img.getdata())).reshape(w, h, len(pixels[0])) # determine how many channels an image has

    total_count = {}
    most_vibrant = None

    for y in range(0, h):
        for x in range(0, w):
            pixel = pixels[x][y]

            if len(pixel) > 3:
                if pixel[3] < 255: #transparent
                    continue

            rgb = rgb_to_str(pixel)
            hsv = rgb_to_hsv(pixel)

            if rgb in total_count.keys():
                total_count[rgb] += 1

                if is_vibrant(hsv):
                    if (most_vibrant == None or
                        total_count[rgb] > total_count[most_vibrant]):
                            most_vibrant = rgb
            else:
                nearest_key = {
                    "key": None,
                    "delta": 255
                }

                for k, _ in total_count.items():
                    near, delta = is_near_rgb(pixel, str_to_rgb(k))

                    # :D
                    if (near and
                        delta < nearest_key["delta"] or delta == nearest_key["delta"] and
                            total_count[k] >  total_count[nearest_key["key"]]):
                                nearest_key["key"] = k
                                nearest_key["delta"] = delta

                if nearest_key["key"] == None:
                    total_count[rgb] = 1
                else:
                    total_count[nearest_key["key"]] += 1

                    hsv = rgb_to_hsv(str_to_rgb(nearest_key["key"]))

                    if is_vibrant(hsv):
                        if (most_vibrant == None or
                            total_count[nearest_key["key"]] > total_count[most_vibrant]):
                                most_vibrant = nearest_key["key"]

    if most_vibrant != None:
        rgb = str_to_rgb(most_vibrant)
    else:
        rgb = str_to_rgb(max(total_count, key=total_count.get))

    return discord.Color.from_rgb(rgb[0], rgb[1], rgb[2])
