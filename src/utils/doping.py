from re import sub

from texture import Wafer, Texture
from collections import deque

si_types = [
    "si",
    "p_doped_si",
    "n_doped_si",
    "p_doped_si_drive_in",
    "n_doped_si_drive_in",
    "slight_doped_p_si",
    "slight_doped_n_si",
]


def _dope_surface_px(
    tex: Texture, row, px, substrates, doped_mat, dope_type, penetrate=False
):
    out_mats = deque()
    out_thicknesses = deque()
    run_thickness_sum = 0
    for layer in range(len(tex.mats[row][px])):
        thickness = tex.thicknesses[row][px][layer]
        if (
            tex.mats[row][px][layer] in substrates and run_thickness_sum < 2000
        ):  # idk man
            out_mats.append(doped_mat[dope_type])
            out_thicknesses.append(thickness * 0.05)
            out_mats.append(tex.mats[row][px][layer])
            out_thicknesses.append(thickness * 0.95)
        else:
            out_mats.append(tex.mats[row][px][layer])
            out_thicknesses.append(thickness)
        run_thickness_sum += thickness
    tex.mats[row][px] = out_mats
    tex.thicknesses[row][px] = out_thicknesses


def dope_surface(
    texture: Wafer,
    dope_type: str,
    substrate: list | None = None,
    doped_mat: dict | None = None,
    penetrate=False,
):
    if not substrate:
        substrate = si_types
    if not doped_mat:
        doped_mat = {"p": "p_doped_si", "n": "n_doped_si"}
    for row in range(texture.h):
        for px in range(texture.w):
            _dope_surface_px(
                texture.base_tex, row, px, substrate, doped_mat, dope_type, penetrate
            )
            _dope_surface_px(
                texture.exposed_tex, row, px, substrate, doped_mat, dope_type, penetrate
            )


def _drive_in_px(tex: Texture, row, px, doped_mat_names, substrate, driven):
    tmp_mat = deque()
    tmp_thickness = deque()
    skip = False
    for index in range(len(tex.mats[row][px]) - 1):
        if skip:
            skip = False
            continue
        this_mat = tex.mats[row][px][index]
        below_mat = tex.mats[row][px][index + 1]

        if this_mat in doped_mat_names and below_mat in substrate:
            tmp_mat.append(driven[doped_mat_names.index(tex.mats[row][px][index])])
            tmp_mat.append(below_mat)
            tmp_thickness.append(
                (tex.thicknesses[row][px][index] + tex.thicknesses[row][px][index + 1])
                * 0.75
            )
            tmp_thickness.append(
                (tex.thicknesses[row][px][index] + tex.thicknesses[row][px][index + 1])
                * 0.25
            )
            skip = True
        else:
            tmp_mat.append(tex.mats[row][px][index])
            tmp_thickness.append(tex.thicknesses[row][px][index])
    if not skip:
        tmp_mat.append(tex.mats[row][px][-1])
        tmp_thickness.append(tex.thicknesses[row][px][-1])
    tex.mats[row][px] = tmp_mat
    tex.thicknesses[row][px] = tmp_thickness


def drive_in(
    texture: Wafer,
    doped_mat_names: list[str] | None = None,
    substrate: list[str] | None = None,
    driven: list[str] | None = None,
):
    if not doped_mat_names:
        doped_mat_names = ["p_doped_si", "n_doped_si"]
    if not driven:
        driven = ["p_doped_si_drive_in", "n_doped_si_drive_in"]
    if not substrate:
        substrate = si_types
    for row in range(texture.h):
        for px in range(texture.w):
            _drive_in_px(texture.base_tex, row, px, doped_mat_names, substrate, driven)
            _drive_in_px(
                texture.exposed_tex, row, px, doped_mat_names, substrate, driven
            )


def _intermetallics_px(tex: Texture, row, px, mat_a, mat_b, mixed):
    copy_mat, copy_thickness = deque(), deque()
    skip = False
    for index in range(len(tex.mats[row][px]) - 1, 1, -1):
        if skip:
            skip = False
            continue
        copy_mat.appendleft(tex.mats[row][px][index])
        if (
            tex.mats[row][px][index] in mat_a and tex.mats[row][px][index - 1] in mat_b
        ) or (
            tex.mats[row][px][index] in mat_b and tex.mats[row][px][index - 1] in mat_a
        ):
            copy_mat.appendleft(mixed)
            copy_thickness.append(tex.thicknesses[row][px][index] * 0.9)
            copy_thickness.append(
                tex.thicknesses[row][px][index] * 0.1
                + tex.thicknesses[row][px][index - 1] * 0.2
            )
            copy_thickness.append(tex.thicknesses[row][px][index - 1] * 0.8)
            skip = True
        else:
            copy_thickness.appendleft(tex.thicknesses[row][px][index])
    if not skip:
        copy_mat.appendleft(tex.mats[row][px][0])
        copy_thickness.appendleft(tex.thicknesses[row][px][0])
    tex.mats[row][px] = copy_mat
    tex.thicknesses[row][px] = copy_thickness


def intermetallics(texture: Wafer, mat_a: str | list, mat_b: str | list, mixed: str):
    if type(mat_a) == str:
        mat_a = [mat_a]
    if type(mat_b) == str:
        mat_b = [mat_b]
    for row in range(texture.h):
        for px in range(texture.w):
            _intermetallics_px(texture.base_tex, row, px, mat_a, mat_b, mixed)
            _intermetallics_px(texture.exposed_tex, row, px, mat_a, mat_b, mixed)
