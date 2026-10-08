import functools
import numpy
import time
import torch

from collections.abc import Callable
from math import inf, acos, exp, pi
from PIL import Image
from refractiveindex import RefractiveIndexMaterial
from tmm_fast import coh_tmm

ior_dict = {
    "Si": RefractiveIndexMaterial(shelf="main", book="Si", page="Franta-25C"),
    "Air": RefractiveIndexMaterial(shelf="other", book="air", page="Ciddor"),
}


COLORPY_RANGE = (380, 780 + 1)


def do_nothing(fun):
    return fun


import csv


def load_references():
    with open("./CIE_xyz_1931_2deg.csv") as response_file:
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
    with open("./CIE_std_illum_D65.csv") as d65_file:
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
def get_complex_ior_fn(
    ior: RefractiveIndexMaterial,
    mod_fn: Callable[
        [Callable[[int], complex]],
        Callable[
            [int], complex
        ],  # what am i even doing??; function that modifies the wavelength -> IOR function; used for color tinting or something
    ] = do_nothing,
):
    get_n, get_k = None, None
    if ior._k_func is None:
        get_k = lambda a: 0
    else:
        get_k = lambda a: ior.get_extinction_coefficient(a)
    if ior._n_func is None:
        get_n = lambda a: 0
    else:
        get_n = lambda a: ior.get_refractive_index(a)
    tmp = lambda a: get_n(a) + get_k(a) * 1j
    return functools.lru_cache(700)(mod_fn(tmp))  # cachemaxxing


@functools.lru_cache
def get_ior_over_wavelengths(start: int, end: int, func: Callable[[int], complex]):
    tmp = []
    for wavelen in range(start, end):
        tmp.append(func(wavelen))
    return tmp


class Texture:
    def __init__(self, w=32, h=32):
        self.mats = [[["Air", "Si", "Air"]] * w] * h
        self.thicknesses = [[[inf, 100000, inf]] * w] * h
        self.w = w
        self.h = h

        self.viewangles = []

        self.view_pos = numpy.array([32, 32, -6])
        for row in range(self.h):
            angle_row = []
            for px in range(self.w):
                coord = numpy.array([row + 0.5, px + 0.5, 0])
                view_vec = coord - self.view_pos
                other = coord - self.view_pos
                other[2] = 0
                view_vec = view_vec / numpy.linalg.norm(view_vec)
                other = other / numpy.linalg.norm(other)
                angle_row.append(pi / 2 - acos(numpy.dot(view_vec, other)))
                print(int((angle_row[-1] * 180 / pi) * 100) / 100, end="\t")
            print()
            self.viewangles.append(angle_row)
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

    def render(self):
        out_pixels = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        all_iors = []
        all_thicknesses = []
        all_thetas = []
        locations = []
        for row in range(self.h):
            for px in range(self.w):
                if ((row + 0.5) - self.h / 2) ** 2 + ((px + 0.5) - self.w / 2) ** 2 > (
                    (self.h + self.w) / 4
                ) ** 2:
                    continue
                locations.append((px, row))
                ior_funcs = [
                    get_complex_ior_fn(ior_dict[mat], red_tint)
                    for mat in self.mats[row][px]
                ]

                iors = []
                for ior_func in ior_funcs:
                    material_indices = get_ior_over_wavelengths(
                        COLORPY_RANGE[0], COLORPY_RANGE[1], ior_func
                    )
                    iors.append(material_indices)
                all_iors.append(iors)
                all_thicknesses.append(self.thicknesses[row][px])
                all_thetas.append(
                    [[self.viewangles[row][px]] * (COLORPY_RANGE[1] - COLORPY_RANGE[0])]
                )
        wavelengths = torch.arange(COLORPY_RANGE[0], COLORPY_RANGE[1])
        with torch.no_grad():  # we're not training a nn here
            spectra = (
                coh_tmm("p", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
                + coh_tmm("s", all_iors, all_thicknesses, all_thetas, wavelengths)["R"]
            ) / 2

        rgb = self.calc_rgb_from_spectra(spectra)
        for pos, color in zip(locations, rgb):
            out_pixels.putpixel(pos, tuple([round(x) for x in color.tolist()]))
        return out_pixels


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
