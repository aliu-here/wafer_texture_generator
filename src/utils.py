from texture import Wafer, root_path
from PIL import Image, ImageOps
import itertools
from collections import deque
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


def gen_photolithography(
    texture: Wafer,
    mask: Image.Image,
    photoresist_mat: str,
    input_name,
    output_name,
    thickness=10000,
):
    texture.deposit_layer(photoresist_mat, thickness)
    save_img(texture, input_name + ".coated")
    texture.mod_layer(photoresist_mat, "exposed_" + photoresist_mat, mask)
    save_img(texture, input_name + ".exposed")
    texture.remove_layer("exposed_" + photoresist_mat)
    save_img(texture, output_name)


def gen_split_lithography(
    texture: Wafer,
    mask: Image.Image,
    photoresist_mat,
    intermediate_name,
    output_name,
):
    texture.mod_layer(photoresist_mat, "exposed_" + photoresist_mat, mask)
    save_img(texture, intermediate_name + ".exposed")
    texture.remove_layer("exposed_" + photoresist_mat)
    save_img(texture, output_name)


def dope_surface(texture: Wafer, dope_type: str, substrate: str = "si"):
    doped_mat = "p_doped_si" if dope_type == "p" else "n_doped_si"
    for row in range(texture.h):
        for px in range(texture.w):
            if texture.base_tex.mats[row][px][0] == substrate:
                thickness = texture.base_tex.thicknesses[row][px][0]
                texture.base_tex.thicknesses[row][px][0] = thickness * 0.95
                texture.base_tex.mats[row][px].appendleft(doped_mat)
                texture.base_tex.thicknesses[row][px].appendleft(0.05 * thickness)
            if texture.exposed_tex.mats[row][px][0] == substrate:
                thickness = texture.exposed_tex.thicknesses[row][px][0]
                texture.exposed_tex.thicknesses[row][px][0] = thickness * 0.95
                texture.exposed_tex.mats[row][px].appendleft(doped_mat)
                texture.exposed_tex.thicknesses[row][px].appendleft(0.05 * thickness)


def drive_in(
    texture: Wafer,
    doped_mat_names: list[str] | None = None,
    substrate: str = "si",
):
    if doped_mat_names == None:
        doped_mat_names = ["p_doped_si", "n_doped_si"]
    for row in range(texture.h):
        for px in range(texture.w):
            tmp_mat = deque()
            tmp_thickness = deque()
            skip = False
            for index in range(len(texture.base_tex.mats[row][px]) - 1):
                if skip:
                    continue
                this_mat = texture.base_tex.mats[row][px][index]
                below_mat = texture.base_tex.mats[row][px][index + 1]

                tmp_mat.append(texture.base_tex.mats[row][px][index])
                if this_mat in doped_mat_names and below_mat == substrate:
                    tmp_thickness.append(
                        texture.base_tex.thicknesses[row][px][index]
                        + texture.base_tex.thicknesses[row][px][index + 1]
                    )
                    skip = True
                else:
                    tmp_thickness.append(texture.base_tex.thicknesses[row][px][index])
            if not skip:
                tmp_mat.append(texture.base_tex.mats[row][px][-1])
                tmp_thickness.append(texture.base_tex.thicknesses[row][px][-1])
            texture.base_tex.mats[row][px] = tmp_mat
            texture.base_tex.thicknesses[row][px] = tmp_thickness

            tmp_mat = deque()
            tmp_thickness = deque()
            skip = False
            for index in range(len(texture.exposed_tex.mats[row][px]) - 1):
                if skip:
                    continue
                this_mat = texture.exposed_tex.mats[row][px][index]
                below_mat = texture.exposed_tex.mats[row][px][index + 1]

                tmp_mat.append(texture.exposed_tex.mats[row][px][index])
                if this_mat in doped_mat_names and below_mat == substrate:
                    tmp_thickness.append(
                        texture.exposed_tex.thicknesses[row][px][index]
                        + texture.exposed_tex.thicknesses[row][px][index + 1]
                    )
                    skip = True
                else:
                    tmp_thickness.append(
                        texture.exposed_tex.thicknesses[row][px][index]
                    )
            if not skip:
                tmp_mat.append(texture.exposed_tex.mats[row][px][-1])
                tmp_thickness.append(texture.exposed_tex.thicknesses[row][px][-1])
            texture.exposed_tex.mats[row][px] = tmp_mat
            texture.exposed_tex.thicknesses[row][px] = tmp_thickness


def get_fraction_of_pattern(
    pattern: Image.Image, total_steps, current_step, invert=False, scaling=1.0
):  # this is stupid
    out_tex = Image.new("RGBA", pattern.size, (0, 0, 0, 0))
    counter = 0
    width, height = pattern.size
    for row in range(height):
        for px in range(width):
            pxl = pattern.getpixel((px, row))
            if pxl[3] != 0:
                if counter == current_step:
                    out_tex.putpixel((px, row), pxl)
                counter += 1
                counter %= total_steps
            pxl = out_tex.getpixel((px, row))
            if invert:
                pxl = tuple([255 - x for x in pxl])
            pxl = tuple([int(scaling * x) for x in pxl])
            out_tex.putpixel((px, row), pxl)

    return out_tex
