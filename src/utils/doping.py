from texture import Wafer
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


def dope_surface(texture: Wafer, dope_type: str, substrate: list | None = None):
    if not substrate:
        substrate = si_types
    doped_mat = "p_doped_si" if dope_type == "p" else "n_doped_si"
    for row in range(texture.h):
        for px in range(texture.w):
            if texture.base_tex.mats[row][px][0] in substrate:
                thickness = texture.base_tex.thicknesses[row][px][0]
                texture.base_tex.thicknesses[row][px][0] = thickness * 0.95
                texture.base_tex.mats[row][px].appendleft(doped_mat)
                texture.base_tex.thicknesses[row][px].appendleft(0.05 * thickness)
            if texture.exposed_tex.mats[row][px][0] in substrate and (
                texture.weighting[row][px] > 0
                or texture.base_tex.mats[row][px][0] in substrate
            ):
                thickness = texture.exposed_tex.thicknesses[row][px][0]
                texture.exposed_tex.thicknesses[row][px][0] = thickness * 0.95
                texture.exposed_tex.mats[row][px].appendleft(doped_mat)
                texture.exposed_tex.thicknesses[row][px].appendleft(0.05 * thickness)


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
            tmp_mat = deque()
            tmp_thickness = deque()
            skip = False
            for index in range(len(texture.base_tex.mats[row][px]) - 1):
                if skip:
                    skip = False
                    continue
                this_mat = texture.base_tex.mats[row][px][index]
                below_mat = texture.base_tex.mats[row][px][index + 1]

                if this_mat in doped_mat_names and below_mat in substrate:
                    tmp_mat.append(
                        driven[
                            doped_mat_names.index(texture.base_tex.mats[row][px][index])
                        ]
                    )
                    tmp_mat.append(below_mat)
                    tmp_thickness.append(
                        (
                            texture.base_tex.thicknesses[row][px][index]
                            + texture.base_tex.thicknesses[row][px][index + 1]
                        )
                        * 0.75
                    )
                    tmp_thickness.append(
                        (
                            texture.base_tex.thicknesses[row][px][index]
                            + texture.base_tex.thicknesses[row][px][index + 1]
                        )
                        * 0.25
                    )
                    skip = True
                else:
                    tmp_mat.append(texture.base_tex.mats[row][px][index])
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
                    skip = False
                    continue
                this_mat = texture.exposed_tex.mats[row][px][index]
                below_mat = texture.exposed_tex.mats[row][px][index + 1]

                if this_mat in doped_mat_names and below_mat in substrate:
                    tmp_mat.append(
                        driven[
                            doped_mat_names.index(
                                texture.exposed_tex.mats[row][px][index]
                            )
                        ]
                    )
                    tmp_mat.append(below_mat)
                    tmp_thickness.append(
                        (
                            texture.exposed_tex.thicknesses[row][px][index]
                            + texture.exposed_tex.thicknesses[row][px][index + 1]
                        )
                        * 0.75
                    )
                    tmp_thickness.append(
                        (
                            texture.exposed_tex.thicknesses[row][px][index]
                            + texture.exposed_tex.thicknesses[row][px][index + 1]
                        )
                        * 0.25
                    )
                    skip = True
                else:
                    tmp_mat.append(texture.exposed_tex.mats[row][px][index])
                    tmp_thickness.append(
                        texture.exposed_tex.thicknesses[row][px][index]
                    )
            if not skip:
                tmp_mat.append(texture.exposed_tex.mats[row][px][-1])
                tmp_thickness.append(texture.exposed_tex.thicknesses[row][px][-1])
            texture.exposed_tex.mats[row][px] = tmp_mat
            texture.exposed_tex.thicknesses[row][px] = tmp_thickness
