from texture import Wafer, root_path
from PIL import Image
import misc_utils
from .utils import lithography, doping
import copy


def gen_pic_base():
    wafer = Wafer(32, 32, "slight_doped_p_si")
    pattern = Image.open(
        root_path + "/resources/images/overlay/bjt_pic_base.png"
    ).convert("RGBA")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 4, [0]),
        "novolac_resist",
        "silicon.p_doped",
        "bjt_pic_base.step_one",
    )
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, "bjt_pic_base.step_two")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic_base.step_three")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bjt_pic_base.step_four")
    wafer.deposit_layer("slight_doped_n_si", 20)
    misc_utils.save_img(wafer, "bjt_pic_base.step_five")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 4, [1]),
        "novolac_resist",
        "bjt_pic_base.step_five",
        "bjt_pic_base.step_six",
    )
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, "bjt_pic_base.step_seven")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic_base.step_eight")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bjt_pic_base.step_nine")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 4, [2]),
        "novolac_resist",
        "bjt_pic_base.step_nine",
        "bjt_pic_base.step_ten",
    )
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, "bjt_pic_base.step_eleven")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic_base.step_twelve")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bjt_pic_base.step_thirteen")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 4, [3]),
        "novolac_resist",
        "bjt_pic_base.step_thirteen",
        "bjt_pic_base.step_fourteen",
    )
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, "bjt_pic_base.step_fifteen")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic_base.step_sixteen")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bjt_pic_base.step_seventeen")

    gen_ulpic(copy.deepcopy(wafer))
    gen_lpic(copy.deepcopy(wafer))


def gen_ulpic(wafer):
    pattern = Image.open(root_path + "/resources/images/overlay/bjt_ulpic.png").convert(
        "RGBA"
    )
    wafer.deposit_layer("al", 5)
    misc_utils.save_img(wafer, "bjt_ulpic.step_one")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 1, [0], True),
        "novolac_resist",
        "bjt_ulpic.step_one",
        "bjt_ulpic.step_two",
    )
    wafer.remove_layer("al")
    misc_utils.save_img(wafer, "bjt_ulpic.step_three")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_ulpic.step_four")
    wafer.grow_layer("al2o3", 10, "al")
    misc_utils.save_img(wafer, "bjt_ulpic.step_five")


def gen_lpic(wafer):
    pattern = Image.open(root_path + "/resources/images/overlay/bjt_lpic.png").convert(
        "RGBA"
    )
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 3, [0]),
        "novolac_resist",
        "bjt_ulpic.step_five",
        "bjt_lpic.step_one",
    )
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, "bjt_lpic.step_two")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_lpic.step_three")

    wafer.deposit_layer("si", 20)
    misc_utils.save_img(wafer, "bjt_lpic.step_four")
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, "bjt_lpic.step_five")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 3, [1]),
        "novolac_resist",
        "bjt_lpic.step_five",
        "bjt_lpic.step_six",
    )
    wafer.remove_layer("n_doped_si")
    wafer.remove_layer("si")
    misc_utils.save_img(wafer, "bjt_lpic.step_seven")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_lpic.step_eight")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, "bjt_lpic.step_nine")

    wafer.deposit_layer("phosphosilicate_glass", 3000)
    misc_utils.save_img(wafer, "bjt_lpic.step_ten")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 3, [2]),
        "novolac_resist",
        "bjt_lpic.step_ten",
        "bjt_lpic.step_eleven",
    )
    wafer.remove_layer("phosphosilicate_glass")
    misc_utils.save_img(wafer, "bjt_lpic.step_twelve")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_lpic.step_thirteen")
    gen_pic(copy.deepcopy(wafer))

    wafer.deposit_layer("titanium_nitride", 10)
    misc_utils.save_img(wafer, "bjt_lpic.step_fourteen")

    wafer.deposit_layer("al", 5)
    misc_utils.save_img(wafer, "bjt_lpic.step_fifteen")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 3, [2], True),
        "novolac_resist",
        "bjt_lpic.step_fifteen",
        "bjt_lpic.step_sixteen",
    )
    wafer.remove_layer("al")
    misc_utils.save_img(wafer, "bjt_lpic.step_seventeen")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_lpic.step_eighteen")
    wafer.grow_layer("al2o3", 10, "al")
    misc_utils.save_img(wafer, "bjt_lpic.step_nineteen")


def gen_pic(wafer):
    pattern = Image.open(root_path + "/resources/images/overlay/bjt_pic.png").convert(
        "RGBA"
    )
    wafer.deposit_layer("platinum", 10)
    misc_utils.save_img(wafer, "bjt_pic.step_one")
    doping.drive_in(wafer, ["platinum"], None, ["ptsi"])
    misc_utils.save_img(wafer, "bjt_pic.step_two")
    wafer.remove_layer("platinum")
    misc_utils.save_img(wafer, "bjt_pic.step_three")

    wafer.deposit_layer("titanium_nitride", 10)
    misc_utils.save_img(wafer, "bjt_pic.step_four")

    wafer.deposit_layer("al", 5)
    misc_utils.save_img(wafer, "bjt_pic.step_five")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 3, [0], True),
        "novolac_resist",
        "bjt_pic.step_five",
        "bjt_pic.step_six",
    )
    wafer.remove_layer("al")
    misc_utils.save_img(wafer, "bjt_pic.step_six")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic.step_seven")

    wafer.deposit_layer("phosphosilicate_glass", 100)
    misc_utils.save_img(wafer, "bjt_pic.step_eight")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 2, [1]),
        "novolac_resist",
        "bjt_pic.step_eight",
        "bjt_pic.step_nine",
    )
    wafer.remove_layer("phosphosilicate_glass")
    misc_utils.save_img(wafer, "bjt_pic.step_ten")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic.step_eleven")

    wafer.deposit_layer("al", 5)
    misc_utils.save_img(wafer, "bjt_pic.step_twelve")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(pattern, 2, [1], True),
        "novolac_resist",
        "bjt_pic.step_twelve",
        "bjt_pic.step_thirteen",
    )
    wafer.remove_layer("al")
    misc_utils.save_img(wafer, "bjt_pic.step_fourteen")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, "bjt_pic.step_fifteen")


if __name__ == "__main__":
    gen_pic_base()
