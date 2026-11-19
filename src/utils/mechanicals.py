from texture import Wafer, Texture
from PIL import Image
from . import misc_utils
from collections import deque


def gen_cmp(texture: Wafer, output_name: str):
    min_height = min(
        sum(texture.exposed_tex.thicknesses[0][0]),
        sum(texture.base_tex.thicknesses[0][0]),
    )

    for row in range(texture.h):
        for px in range(texture.w):
            min_height = min(
                min_height,
                min(
                    sum(texture.exposed_tex.thicknesses[row][px]),
                    sum(texture.base_tex.thicknesses[row][px]),
                ),
            )

    gen_cmp_thickness(texture, output_name, min_height)


def _gen_cmp_thickness_px(tex: Texture, row, px, output_name, thickness_to_achieve):
    running_sum = 0
    tmp_mats = deque()
    tmp_thickness = deque()
    for thickness, mat in zip(
        [x for x in list(tex.thicknesses[row][px])[::-1]],  # I LOVE KLUDGES!!!!! :TROL:
        [x for x in list(tex.mats[row][px])[::-1]],
    ):
        running_sum += thickness
        if running_sum >= thickness_to_achieve:
            tmp_thickness.appendleft(thickness - (running_sum - thickness_to_achieve))
            tmp_mats.appendleft(mat)
            break
        else:
            tmp_thickness.appendleft(thickness)
            tmp_mats.appendleft(mat)
    tex.thicknesses[row][px] = tmp_thickness
    tex.mats[row][px] = tmp_mats


def gen_cmp_thickness(texture: Wafer, output_name: str, thickness_to_achieve: int):
    for row in range(texture.h):
        for px in range(texture.w):
            _gen_cmp_thickness_px(
                texture.base_tex, row, px, output_name, thickness_to_achieve
            )
            _gen_cmp_thickness_px(
                texture.exposed_tex, row, px, output_name, thickness_to_achieve
            )
    misc_utils.save_img(texture, output_name)


def gen_backgrinding(texture: Wafer, output_name: str):
    for row in range(texture.h):
        for px in range(texture.w):
            texture.base_tex.thicknesses[row][px][-1] *= 0.1
            texture.exposed_tex.thicknesses[row][px][-1] *= 0.1
