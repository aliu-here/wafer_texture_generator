import functools
import numpy
import time
import torch

from math import inf, acos, exp, pi
from PIL import Image
from tmm_fast import coh_tmm
from mat_defs import ior_dict
from collections import deque
from collections.abc import Callable
import itertools
import warnings

COLORPY_RANGE = (380, 780 + 1)

import csv

torch.no_grad()  # no autograd needed
root_path = "/".join(__file__.split("/")[:-2])


def load_references():
    with open(root_path + "/resources/CIE_xyz_1931_2deg.csv") as response_file:
        reader = csv.reader(response_file, delimiter=",")
        x, y, z = [], [], []
        for row in reader:
            if int(row[0]) >= COLORPY_RANGE[0] and int(row[0]) < COLORPY_RANGE[1]:
                x.append(float(row[1]))
                y.append(float(row[2]))
                z.append(float(row[3]))
        response_funcs = (
            torch.stack((torch.tensor(x), torch.tensor(y), torch.tensor(z)))
            .to(dtype=torch.double)
            .transpose(0, 1)
        )
    with open(root_path + "/resources/CIE_std_illum_D65.csv") as d65_file:
        reader = csv.reader(d65_file, delimiter=",")
        vals = []
        for row in reader:
            if int(row[0]) >= COLORPY_RANGE[0] and int(row[0]) < COLORPY_RANGE[1]:
                vals.append(float(row[1]))
        d65 = torch.tensor(vals, dtype=torch.double)
    return response_funcs, d65


response_funcs, d65 = load_references()
N = torch.dot(d65, response_funcs.transpose(0, 1)[1])


@functools.lru_cache
def get_ior_over_wavelengths(start: int, end: int, func: Callable[[int], complex]):
    tmp = []
    for wavelen in range(start, end):
        tmp.append(func(wavelen))
    return tmp


class Texture:
    def __init__(self, w=32, h=32, base_mat="si"):
        self.mats = []
        self.thicknesses = []

        self.top_bottom_layer = deque(["air"])
        self.top_bottom_thickness = deque([inf])
        self.padding_layer = deque(["air"])
        self.padding_layer_thickness = deque([1.0])

        self.w = w
        self.h = h

        self.viewangles = []

        self.view_pos = numpy.array([32, 32, -32])
        for row in range(self.h):
            angle_row = []
            mats = []
            thicknesses = []
            for px in range(self.w):
                coord = numpy.array([row + 0.5, px + 0.5, 0])
                view_vec = coord - self.view_pos
                other = coord - self.view_pos
                other[2] = 0
                view_vec = view_vec / numpy.linalg.norm(view_vec)
                other = other / numpy.linalg.norm(other)
                angle_row.append(pi / 2 - acos(numpy.dot(view_vec, other)))

                mats.append(deque([base_mat]))
                thicknesses.append(
                    deque(
                        [
                            100000,
                        ]
                    )
                )
            self.viewangles.append(angle_row)
            self.mats.append(mats)
            self.thicknesses.append(thicknesses)

        self.illum = d65

    def calc_spectra(self):
        all_iors = []
        all_thicknesses = []
        all_thetas = []
        locations = []
        max_ior_num = 0
        for row in range(self.h):
            for px in range(self.w):
                max_ior_num = max(max_ior_num, len(self.mats[row][px]))
        for row in range(self.h):
            for px in range(self.w):
                locations.append((row, px))
                ior_funcs = [
                    ior_dict[mat.lower()]
                    for mat in self.top_bottom_layer
                    + self.padding_layer * (max_ior_num - len(self.mats[row][px]))
                    + self.mats[row][px]
                    + self.top_bottom_layer
                ]

                iors = []
                for ior_func in ior_funcs:
                    material_indices = get_ior_over_wavelengths(
                        COLORPY_RANGE[0], COLORPY_RANGE[1], ior_func
                    )
                    iors.append(material_indices)
                all_iors.append(iors)
                all_thicknesses.append(
                    self.top_bottom_thickness
                    + self.padding_layer_thickness
                    * (max_ior_num - len(self.mats[row][px]))
                    + self.thicknesses[row][px]
                    + self.top_bottom_thickness
                )
                all_thetas.append(
                    [[self.viewangles[row][px]] * (COLORPY_RANGE[1] - COLORPY_RANGE[0])]
                )
        all_iors = torch.tensor(all_iors)
        all_thicknesses = torch.tensor(all_thicknesses)
        all_thetas = torch.tensor(all_thetas)
        wavelengths = torch.arange(COLORPY_RANGE[0], COLORPY_RANGE[1])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            spectra = (
                coh_tmm("p", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
                + coh_tmm("s", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
            ) / 2

        return spectra, locations


class Wafer:
    def __init__(self, w=32, h=32):
        self.w = w
        self.h = h
        self.base_tex = Texture(w, h)
        self.exposed_tex = Texture(w, h)
        self.weighting = torch.zeros((32, 32))

    def out_circle(self, row, px):
        return ((row + 0.5) - self.h / 2) ** 2 + ((px + 0.5) - self.w / 2) ** 2 > (
            (self.h + self.w) / 4 - 2
        ) ** 2

    def calc_rgb_from_spectra(self, spectra):
        spectra *= d65.tile((spectra.shape[0], 1, 1))
        xyz = torch.matmul(spectra, response_funcs).transpose(-1, -2) / N
        rgb = (
            torch.matmul(
                torch.tensor(
                    [
                        [3.2406, -1.5372, -0.4986],
                        [-0.9689, 1.8758, 0.0415],
                        [0.0557, -0.2040, 1.0570],
                    ],
                    dtype=torch.double,
                ),
                xyz,
            ).squeeze()
            * 255
        )
        return rgb

    def render(self):
        base_spec, locs = self.base_tex.calc_spectra()
        exposed_spec, _ = self.exposed_tex.calc_spectra()

        spec = base_spec * (
            torch.ones((self.w * self.h, 1, 1))
            - self.weighting.flatten().reshape(self.w * self.h, 1, 1)
        ) + exposed_spec * self.weighting.flatten().reshape(self.w * self.h, 1, 1)

        tex = Image.new("RGBA", (self.w, self.h))

        colors = self.calc_rgb_from_spectra(spec)

        for rgb, loc in zip(colors, locs):
            if self.out_circle(loc[0], loc[1]):
                continue
            tex.putpixel(
                (loc[1], loc[0]), tuple([int(x) for x in rgb.tolist()] + [255])
            )
        return tex

    def deposit_layer(self, material, thickness):
        for row in range(self.h):
            for px in range(self.w):
                self.base_tex.mats[row][px].appendleft(material)
                self.base_tex.thicknesses[row][px].appendleft(thickness)
                self.exposed_tex.mats[row][px].appendleft(material)
                self.exposed_tex.thicknesses[row][px].appendleft(thickness)

    def mod_layer(self, material, alt_material, mask):
        for row in range(self.h):
            for px in range(self.w):
                if (
                    mask.getpixel((px, row))[3] != 0
                ):  # bc we're doing fractions of the full texture, don't overwrite if
                    # there's no pattern there since there might be one from an earlier
                    # patterning step
                    self.weighting[row][px] = mask.getpixel((px, row))[3] / 255
                    if self.exposed_tex.mats[row][px][0] == material:
                        self.exposed_tex.mats[row][px][0] = alt_material

    def grow_layer(self, material, thickness, substrates: str | list[str]):
        if type(substrates) == str:
            substrates = [substrates]
        for row in range(self.h):
            for px in range(self.w):
                if self.base_tex.mats[row][px][0] in substrates:
                    self.base_tex.mats[row][px].appendleft(material)
                    self.base_tex.thicknesses[row][px].appendleft(thickness)
                if self.exposed_tex.mats[row][px][0] in substrates:
                    self.exposed_tex.mats[row][px].appendleft(material)
                    self.exposed_tex.thicknesses[row][px].appendleft(thickness)

    def remove_layer(self, material, etching=True):
        for row in range(self.h):
            for px in range(self.w):
                if etching:
                    if self.base_tex.mats[row][px][0] == material:
                        self.base_tex.mats[row][px] = deque(
                            itertools.islice(self.base_tex.mats[row][px], 1, None)
                        )
                        self.base_tex.thicknesses[row][px] = deque(
                            itertools.islice(
                                self.base_tex.thicknesses[row][px], 1, None
                            )
                        )
                    if self.exposed_tex.mats[row][px][0] == material:
                        self.exposed_tex.mats[row][px] = deque(
                            itertools.islice(self.exposed_tex.mats[row][px], 1, None)
                        )
                        self.exposed_tex.thicknesses[row][px] = deque(
                            itertools.islice(
                                self.exposed_tex.thicknesses[row][px], 1, None
                            )
                        )
                else:  # hang on i have to water the shitcode
                    try:
                        idx = self.base_tex.mats[row][px].index(material)
                        self.base_tex.mats[row][px] = deque(
                            itertools.islice(self.base_tex.mats[row][px], idx + 1, None)
                        )
                        self.base_tex.thicknesses[row][px] = deque(
                            itertools.islice(
                                self.base_tex.thicknesses[row][px], idx + 1, None
                            )
                        )
                    except ValueError:
                        pass  # dgaf if can't find

                    try:
                        idx = self.exposed_tex.mats[row][px].index(material)
                        self.exposed_tex.mats[row][px] = deque(
                            itertools.islice(
                                self.exposed_tex.mats[row][px], idx + 1, None
                            )
                        )
                        self.exposed_tex.thicknesses[row][px] = deque(
                            itertools.islice(
                                self.exposed_tex.thicknesses[row][px], idx + 1, None
                            )
                        )
                    except ValueError:
                        pass


if __name__ == "__main__":
    tex = Wafer(32, 32)
    tex.render().show()
