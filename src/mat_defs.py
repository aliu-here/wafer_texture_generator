from collections.abc import Callable
from math import exp
from operator import ior
from refractiveindex import RefractiveIndexMaterial

import functools


def do_nothing(fun):
    return fun


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
    wl_range = ior.get_wl_range(unit="nm")
    tmp = lambda a: (  # horrific kludge
        get_n(a) + get_k(a) * 1j
        if a >= wl_range[0] and a <= wl_range[1]
        else get_n(wl_range[0]) + get_k(wl_range[0]) * 1j
        if a < wl_range[0]
        else get_n(wl_range[1]) + get_k(wl_range[1]) * 1j
    )
    return functools.lru_cache(402)(mod_fn(tmp))  # cachemaxxing


@functools.lru_cache
def gaussian(peak_val, mean, stddev):
    return lambda x: peak_val * exp(-((x - mean) ** 2) / (2 * stddev**2))


def multiply_by_val(amount):
    return lambda fn: lambda x: (fn(x) - 1) * amount + 1


def exponential(decay_rate, y_int):
    return lambda x: pow((x - 380) / 400, decay_rate) * (y_int - 1) + 1


ior_dict = {
    "si": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Si", page="Franta-25C")
    ),
    "p_doped_si": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(2, 750, 300)(wavelength)
        )
    ),
    "n_doped_si": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(2, 450, 300)(wavelength)
        )
    ),
    "p_doped_si_drive_in": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(4, 750, 300)(wavelength)
        )
    ),
    "n_doped_si_drive_in": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(4, 450, 300)(wavelength)
        )
    ),
    "slight_doped_n_si": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(0.5, 450, 300)(wavelength)
        )
    ),
    "slight_doped_p_si": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) + gaussian(0.5, 750, 300)(wavelength)
        )
    ),
    "air": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="other", book="air", page="Ciddor")
    ),
    "si3n4": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Si3N4", page="Philipp"),
    ),
    "sio2": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="SiO2", page="Franta-25C")
    ),
    "novolac_resist": functools.lru_cache(402)(
        lambda wavelength: (
            exponential(0.98, 1.55)(wavelength) + gaussian(1.5, 500, 200)(wavelength)
        )
    ),  # kind of made up values
    "exposed_novolac_resist": functools.lru_cache(402)(
        lambda wavelength: (
            multiply_by_val(1 / 3)(ior_dict["novolac_resist"])(wavelength)
            + gaussian(3, 700, 200)(wavelength)
        )
    ),
    "methacrylate_resist": functools.lru_cache(402)(
        lambda wavelength: (
            get_complex_ior_fn(
                RefractiveIndexMaterial(
                    shelf="other", book="Microchem495", page="specs"
                )
            )(wavelength)
            + gaussian(1, 450, 200)(wavelength)
        )
    ),
    "exposed_methacrylate_resist": functools.lru_cache(402)(
        lambda wavelength: (
            gaussian(1, 700, 200)(wavelength)
            + ior_dict["methacrylate_resist"](wavelength)
        )
    ),
    "methacrylate_resist_trilayer": functools.lru_cache(402)(
        lambda wavelength: (
            get_complex_ior_fn(
                RefractiveIndexMaterial(
                    shelf="other", book="Microchem495", page="specs"
                )
            )(wavelength)
            + gaussian(1, 450, 200)(wavelength)
        )
    ),
    "exposed_methacrylate_resist_trilayer": functools.lru_cache(402)(
        lambda wavelength: (
            gaussian(1, 700, 200)(wavelength)
            + ior_dict["methacrylate_resist"](wavelength)
        )
    ),
    "al": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Al", page="Cheng")
    ),
    "al2o3": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Al2O3", page="Boidin")
    ),
    "phosphosilicate_glass": lambda wavelength: (
        get_complex_ior_fn(
            RefractiveIndexMaterial(shelf="glass", book="fused_silica", page="Malitson")
        )(wavelength)
        + gaussian(0.5, 450, 300)(wavelength)
    ),
    "titanium_nitride": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="TiN", page="Schnabel")
    ),
    "platinum": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Pt", page="Werner")
    ),
    "ptsi": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["platinum"](wavelength) * 0.5 + ior_dict["si"](wavelength) * 0.5
        )
    ),
    "hfo2": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="HfO2", page="Franta")
    ),
    "silicon_oxynitride": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si3n4"](wavelength) * 0.5 + ior_dict["sio2"](wavelength) * 0.5
        )
    ),
    "spin_on_carbon": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="C", page="Larruquert")
    ),
    "ash": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="other", book="propane_soot", page="Dlazell")
    ),
    "sige": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="other", book="Si-Ge", page="Jellison-48")
    ),
    "slight_doped_p_sige": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["sige"](wavelength) + gaussian(0.5, 750, 300)(wavelength)
        )
    ),
    "p_doped_sige": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["sige"](wavelength) + gaussian(2, 750, 300)(wavelength)
        )
    ),
    "ni": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Ni", page="Werner")
    ),
    "nisi": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) * 1 / 2 + ior_dict["ni"](wavelength) * 1 / 2
        )
    ),
    "ni2si": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["si"](wavelength) * 1 / 3 + ior_dict["ni"](wavelength) * 2 / 3
        )
    ),
    "tungsten": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="W", page="Werner-DFT")
    ),
    "polyhydroxystyrene_resist_trilayer": functools.lru_cache(402)(
        lambda wavelength: (
            exponential(0.75, 2)(wavelength) + gaussian(0.2, 500, 200)(wavelength)
        )
    ),
    "exposed_polyhydroxystyrene_resist_trilayer": functools.lru_cache(402)(
        lambda wavelength: (
            multiply_by_val(1 / 3)(ior_dict["novolac_resist"])(wavelength)
            + gaussian(2, 700, 200)(wavelength)
        )
    ),
    "silicon_carbide": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="SiC", page="Larruquert")
    ),
    "silicon_oxycarbide_hydride": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["silicon_carbide"](wavelength).real
            + ior_dict["silicon_carbide"](wavelength).imag * 0.2
        )
    ),
    "tantalum_nitride": functools.lru_cache(402)(
        lambda wavelength: (
            exponential(0.75, 2)(wavelength) + gaussian(0.2, 600, 100)(wavelength)
        )
    ),
    "tantalum": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Ta", page="Werner")
    ),
    "copper": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Cu", page="McPeak")
    ),
    "ti": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Ti", page="Palm")
    ),
    "alti": functools.lru_cache(402)(
        lambda wavelength: (
            ior_dict["al"](wavelength) * 1 / 2 + ior_dict["ti"](wavelength) * 1 / 2
        )
    ),
    "chromium": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Cr", page="Johnson")
    ),
    "tin": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Sn", page="Golovashkin-293K")
    ),
    "polysilicon": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Si", page="Pierce")
    ),
}
