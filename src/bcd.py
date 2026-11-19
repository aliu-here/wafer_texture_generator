from numpy import ma

from texture import Wafer, root_path
from PIL import Image
from utils import lithography, doping, mechanicals, misc_utils
import copy
import cmos


def bcd_base():
    mask_pattern = Image.open(
        root_path + "/resources/images/overlay/bcd_base.png"
    ).convert("RGBA")
    wafer = Wafer(32, 32, "slight_doped_p_si")
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, "bcd_base.step_one")
    wafer.deposit_layer("p_doped_si", 200)
    misc_utils.save_img(wafer, "bcd_base.step_two")

    # n well
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [2, 4]),
        "novolac_resist",
        "bcd_base.step_two",
        "bcd_base.step_three",
    )
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, "bcd_base.step_four")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bcd_base.step_five")

    # p well
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [5, 7, 8]),
        "novolac_resist",
        "bcd_base.step_five",
        "bcd_base.step_six",
    )
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, "bcd_base.step_seven")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bcd_base.step_eight")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bcd_base.step_nine")

    # dti
    wafer.grow_layer("sio2", 20)
    misc_utils.save_img(wafer, "bcd_base.step_ten")
    wafer.deposit_layer("si3n4", 100)
    misc_utils.save_img(wafer, "bcd_base.step_eleven")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 1, [0], True, rounding=True),
        "polyhydroxystyrene_resist_trilayer",
        "bcd_base.step_eleven",
        "bcd_base.step_twelve",
    )
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, "bcd_base.step_thirteen")
    wafer.remove_layer("sio2")
    misc_utils.save_img(wafer, "bcd_base.step_fourteen")
    wafer.etch_layer_thickness(1500)
    misc_utils.save_img(wafer, "bcd_base.step_fifteen")
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, "bcd_base.step_sixteen")
    wafer.remove_layer("polyhydroxystyrene_resist_trilayer")
    misc_utils.save_img(wafer, "bcd_base.step_seventeen")
    wafer.grow_layer("sio2", 500)
    misc_utils.save_img(wafer, "bcd_base.step_eighteen")
    wafer.deposit_layer("silicon", 1000)
    misc_utils.save_img(wafer, "bcd_base.step_nineteen")
    mechanicals.gen_cmp_thickness(
        wafer, "bcd_base.step_twenty", 100000 + 200 + 20 + 100
    )

    # sti
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [0, 9]),
        "polyhydroxystyrene_resist",
        "bcd_base.step_twenty",
        "bcd_base.step_twenty_one",
    )
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, "bcd_base.step_twenty_two")
    wafer.remove_layer("sio2")
    misc_utils.save_img(wafer, "bcd_base.step_twenty_three")
    wafer.etch_layer_thickness(500)
    misc_utils.save_img(wafer, "bcd_base.step_twenty_four")
    wafer.remove_layer("polyhydroxystyrene_resist")
    misc_utils.save_img(wafer, "bcd_base.step_twenty_five")
    wafer.grow_layer("sio2", 30)
    misc_utils.save_img(wafer, "bcd_base.step_twenty_six")
    wafer.deposit_layer("sio2", 600)
    misc_utils.save_img(wafer, "bcd_base.step_twenty_seven")

    # more doping
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [1, 2, 4]),
        "polyhydroxystyrene_resist",
        "bcd_base.step_twenty_seven",
        "bcd_base.step_twenty_eight",
    )
    doping.dope_surface(wafer, "p", penetrate=True)
    misc_utils.save_img(wafer, "bcd_base.step_twenty_nine")
    wafer.remove_layer("polyhydroxystyrene_resist")
    misc_utils.save_img(wafer, "bcd_base.step_thirty")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bcd_base.step_thirty_one")

    # wells
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [5, 7]),
        "polyhydroxystyrene_resist",
        "bcd_base.step_thirty_one",
        "bcd_base.step_thirty_two",
    )
    doping.dope_surface(wafer, "n", penetrate=True)
    misc_utils.save_img(wafer, "bcd_base.step_thirty_three")
    wafer.remove_layer("polyhydroxystyrene_resist")
    misc_utils.save_img(wafer, "bcd_base.step_thirty_four")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [2, 4]),
        "polyhydroxystyrene_resist",
        "bcd_base.step_thirty_four",
        "bcd_base.step_thirty_five",
    )
    doping.dope_surface(wafer, "p", penetrate=True)
    misc_utils.save_img(wafer, "bcd_base.step_thirty_six")
    wafer.remove_layer("polyhydroxystyrene_resist")
    misc_utils.save_img(wafer, "bcd_base.step_thirty_seven")


def gen_all():
    bcd_base()
