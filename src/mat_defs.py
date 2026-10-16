from collections.abc import Callable
from math import exp
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
    tmp = lambda a: get_n(a) + get_k(a) * 1j
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
    "al": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Al", page="Cheng")
    ),
    "al2o3": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Al2O3", page="Boidin")
    ),
}
