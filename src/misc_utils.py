from PIL import Image
from texture import Wafer, root_path
import os


def save_img(wafer: Wafer, metaitem_name: str, regen=False):
    base_path = f"{root_path}/generated/wafer/"
    out_file = base_path + "/".join(metaitem_name.split(".")) + ".png"
    if os.path.exists(out_file) and not regen:
        print(f"metaitem {metaitem_name} already saved!\t\t\t\t", end="\r")
        return
    if not os.path.isdir("/".join(out_file.split("/")[:-1])):
        os.makedirs("/".join(out_file.split("/")[:-1]))
    wafer.render().save(out_file)
    print(f"metaitem {metaitem_name} saved!\t\t\t\t", end="\r")


def get_fraction_of_pattern(
    pattern: Image.Image, total_steps, included_steps: list, invert=False, scaling=1.0
):  # this is stupid
    out_tex = Image.new("RGBA", pattern.size, (0, 0, 0, 0))
    counter = 0
    width, height = pattern.size
    for row in range(height):
        for px in range(width):
            pxl = pattern.getpixel((px, row))
            if pxl[3] != 0:
                if counter in included_steps:
                    out_tex.putpixel((px, row), pxl)
                counter += 1
                counter %= total_steps
            pxl = out_tex.getpixel((px, row))
            if invert:
                pxl = tuple([255 - x for x in pxl])
            pxl = tuple([int(scaling * x) for x in pxl])
            out_tex.putpixel((px, row), pxl)

    return out_tex
