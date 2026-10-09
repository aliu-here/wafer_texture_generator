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
    def __init__(self, w=32, h=32, base_mat="Si"):
        self.mats = []
        self.thicknesses = []

        self.top_bottom_layer = deque(["air"])
        self.top_bottom_thickness = deque([inf])

        self.not_total_covered = []
        self.percent_covered = []
        self.alt_mat = []
        self.w = w
        self.h = h

        self.viewangles = []

        self.view_pos = numpy.array([32, 32, -6])
        for row in range(self.h):
            angle_row = []
            mats = []
            thicknesses = []
            not_total_covered = []
            percent_covered = []
            alt_mat = []
            for px in range(self.w):
                coord = numpy.array([row + 0.5, px + 0.5, 0])
                view_vec = coord - self.view_pos
                other = coord - self.view_pos
                other[2] = 0
                view_vec = view_vec / numpy.linalg.norm(view_vec)
                other = other / numpy.linalg.norm(other)
                angle_row.append(pi / 2 - acos(numpy.dot(view_vec, other)))

                mats.append(deque(["Si"]))
                thicknesses.append(
                    deque(
                        [
                            100000,
                        ]
                    )
                )
                not_total_covered.append(deque([0, 0, 0]))
                percent_covered.append(1)
                alt_mat.append(deque(["air", "air", "air"]))
            self.viewangles.append(angle_row)
            self.mats.append(mats)
            self.thicknesses.append(thicknesses)
            self.not_total_covered.append(not_total_covered)
            self.percent_covered.append(percent_covered)
            self.alt_mat.append(alt_mat)

        self.illum = d65

    def calc_rgb_from_spectra(self, spectra):
        spectra *= self.illum.tile((spectra.shape[0], 1, 1))
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

    def in_circle(self, row, px):
        return ((row + 0.5) - self.h / 2) ** 2 + ((px + 0.5) - self.w / 2) ** 2 > (
            (self.h + self.w) / 4
        ) ** 2

    def calc_spectra(self):
        all_iors = []
        all_thicknesses = []
        all_thetas = []
        locations = []

        not_total_covered_indices = []
        not_total_covered_iors = []
        not_total_covered_thicknesses = []
        not_total_covered_percents = []
        for row in range(self.h):
            for px in range(self.w):
                if self.in_circle(row, px):
                    continue
                locations.append((px, row))
                ior_funcs = [
                    ior_dict[mat.lower()]
                    for mat in self.top_bottom_layer
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
                    + self.thicknesses[row][px]
                    + self.top_bottom_thickness
                )
                all_thetas.append(
                    [[self.viewangles[row][px]] * (COLORPY_RANGE[1] - COLORPY_RANGE[0])]
                )

                if sum(self.not_total_covered[row][px]) != 0:
                    not_total_covered_indices.append(len(locations) - 1)
                    ior_funcs = [
                        ior_dict[mat.lower()]
                        if not_total_covered == 0
                        else ior_dict[alt_mat]
                        for not_total_covered, mat, alt_mat in zip(
                            self.not_total_covered[row][px],
                            self.mats[row][px],
                            self.alt_mat[row][px],
                        )
                    ]
                    ior_vals = []
                    for ior_func in ior_funcs:
                        material_indices = get_ior_over_wavelengths(
                            COLORPY_RANGE[0], COLORPY_RANGE[1], ior_func
                        )
                        ior_vals.append(material_indices)
                    not_total_covered_iors.append(ior_vals)
                    not_total_covered_thicknesses.append(self.thicknesses[row][px])
                    not_total_covered_percents.append(self.percent_covered[row][px])
        all_iors += not_total_covered_iors
        all_thicknesses += not_total_covered_thicknesses
        wavelengths = torch.arange(COLORPY_RANGE[0], COLORPY_RANGE[1])
        spectra = (
            coh_tmm("p", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
            + coh_tmm("s", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
        ) / 2

        if len(not_total_covered_indices) > 0:
            spectra, not_covered = spectra.split(len(locations))
            for index, spectrum, percent in zip(
                not_total_covered_indices, not_covered, not_total_covered_percents
            ):
                spectra[index] = spectra[index] * (1 - percent) + spectrum * percent
        return spectra, locations

    def render(self):
        out_pixels = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

        spectra, locations = self.calc_spectra()

        rgb = self.calc_rgb_from_spectra(spectra)
        for pos, color in zip(locations, rgb):
            out_pixels.putpixel(pos, tuple([round(x) for x in color.tolist()]))
        return out_pixels

    def deposit_layer(self, material, thickness, mask=None):
        """expects material as a string, thickness as an int/float (in nm), and mask as a PIL image in RGBA format"""
        for row in range(self.h):
            for px in range(self.w):
                if ((row + 0.5) - self.h / 2) ** 2 + ((px + 0.5) - self.w / 2) ** 2 > (
                    (self.h + self.w) / 4
                ) ** 2:
                    continue
                self.mats[row][px].appendleft(material)
                self.thicknesses[row][px].appendleft(thickness)
                self.not_total_covered[row][px].appendleft(0)
                self.alt_mat[row][px][0] = "air"
        if mask:
            self.mod_top_layer(mask, "air")

    def mod_top_layer(self, mask, changed_material):
        for row in range(self.h):
            for px in range(self.w):
                percent_covered = mask.getpixel((row, px))[4] / 255
                if percent_covered != 0:
                    self.not_total_covered[row][px][0] = 1
                    self.percent_covered[row][px] = (
                        percent_covered  # this is fine since the mask texture stays the same the whole time
                    )
                    self.alt_mat[row][px][0] = changed_material

    def remove_layer(self, material):
        for row in range(self.h):
            for px in range(self.w):
                if ((row + 0.5) - self.h / 2) ** 2 + ((px + 0.5) - self.w / 2) ** 2 > (
                    (self.h + self.w) / 4
                ) ** 2:
                    continue
                index = self.mats[row][px].index(material)
                self.mats[row][px] = self.mats[row][px][index + 1 :]
                self.thicknesses[row][px] = self.thicknesses[row][px][index + 1 :]
                self.not_total_covered[row][px] = self.not_total_covered[row][px][
                    index + 1 :
                ]


def gaussian(peak_val, mean, stddev):
    return lambda x: peak_val * exp(-((x - mean) ** 2) / (2 * stddev**2))


def red_tint(in_fn: Callable[[int], complex]):
    return lambda x: in_fn(x) + gaussian(0, 400, 100)(x)


if __name__ == "__main__":
    tex = Texture(32, 32)
    start = time.time()
    img = tex.render()
    print(f"render time: {time.time() - start}")
    img.show()
