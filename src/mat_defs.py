from collections.abc import Callable
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
    return functools.lru_cache(700)(mod_fn(tmp))  # cachemaxxing


ior_dict = {
    "si": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Si", page="Franta-25C")
    ),
    "air": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="other", book="air", page="Ciddor")
    ),
    "si3n4": get_complex_ior_fn(
        RefractiveIndexMaterial(shelf="main", book="Si3N4", page="Philipp")
    ),
    "novolac_resist": lambda wavelength: (
        15 / ((wavelength - 380) / 400 + 9)
    ),  # kind of made up values
}
