from texture import Wafer, root_path
from PIL import Image
import misc_utils
from .utils import lithography, doping
import copy


def gen_nmos_textures(item_name, nmos_base_copy: Wafer):
    pattern = Image.open(
        root_path + "/resources/images/overlay/" + item_name + ".png"
    ).convert("RGBA")

    pattern1 = misc_utils.get_fraction_of_pattern(pattern, 5, [0, 1, 2, 3], True)
    lithography.gen_split_lithography(
        nmos_base_copy,
        pattern1,
        "novolac_resist",
        f"{item_name}.step_one",
        f"{item_name}.step_two",
    )
    nmos_base_copy.remove_layer("si3n4")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_three")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_four")
    doping.dope_surface(nmos_base_copy, "p")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_five")
    nmos_base_copy.grow_layer("sio2", 400, ["si", "p_doped_si", "n_doped_si"])
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_six")
    nmos_base_copy.remove_layer("si3n4")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_seven")

    pattern2 = misc_utils.get_fraction_of_pattern(pattern, 5, [3])
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern2,
        "novolac_resist",
        f"{item_name}.step_seven",
        f"{item_name}.step_eight",
    )
    doping.dope_surface(nmos_base_copy, "n")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_nine")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_ten")

    pattern3 = misc_utils.get_fraction_of_pattern(pattern, 5, [1], True)
    nmos_base_copy.grow_layer("sio2", 40, ["si", "p_doped_si", "n_doped_si"])
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_eleven")
    nmos_base_copy.deposit_layer("si", 800)
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twelve")
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern3,
        "novolac_resist",
        f"{item_name}.step_twelve",
        f"{item_name}.step_thirteen",
    )
    nmos_base_copy.remove_layer("si")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_fourteen")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_fifteen")

    pattern4 = misc_utils.get_fraction_of_pattern(pattern, 5, [0, 2])
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern4,
        "novolac_resist",
        f"{item_name}.step_fifteen",
        f"{item_name}.step_sixteen",
    )
    nmos_base_copy.remove_layer("sio2")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_seventeen")
    doping.dope_surface(nmos_base_copy, "n")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_eighteen")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_nineteen")
    doping.drive_in(nmos_base_copy)
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty")

    pattern5 = misc_utils.get_fraction_of_pattern(pattern, 5, [4], True)
    nmos_base_copy.deposit_layer("al", 10)  # otherwise it looks bad
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_one")
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern5,
        "novolac_resist",
        f"{item_name}.step_twenty_one",
        f"{item_name}.step_twenty_two",
    )
    nmos_base_copy.remove_layer("al")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_three")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_four")
    nmos_base_copy.grow_layer("al2o3", 100, "al")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_five")


def gen_nmos_dram(nmos_base_copy: Wafer):  # thanks planetme code organization
    item_name = "nmos_dram"
    pattern = Image.open(
        root_path + "/resources/images/overlay/" + item_name + ".png"
    ).convert("RGBA")

    pattern1 = misc_utils.get_fraction_of_pattern(pattern, 4, [1, 2, 3], True)
    lithography.gen_split_lithography(
        nmos_base_copy,
        pattern1,
        "novolac_resist",
        f"{item_name}.step_one",
        f"{item_name}.step_two",
    )
    nmos_base_copy.remove_layer("si3n4")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_three")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_four")
    doping.dope_surface(nmos_base_copy, "p")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_five")
    nmos_base_copy.grow_layer("sio2", 400, ["si", "p_doped_si", "n_doped_si"])
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_six")
    nmos_base_copy.remove_layer("si3n4")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_seven")

    pattern3 = misc_utils.get_fraction_of_pattern(pattern, 4, [2], True)
    nmos_base_copy.grow_layer("sio2", 40, ["si", "p_doped_si", "n_doped_si"])
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_eight")
    nmos_base_copy.deposit_layer("si", 800)
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_nine")
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern3,
        "novolac_resist",
        f"{item_name}.step_nine",
        f"{item_name}.step_ten",
    )
    nmos_base_copy.remove_layer("si")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_eleven")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twelve")

    pattern4 = misc_utils.get_fraction_of_pattern(pattern, 4, [1, 3])
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern4,
        "novolac_resist",
        f"{item_name}.step_twelve",
        f"{item_name}.step_thirteen",
    )
    nmos_base_copy.remove_layer("sio2")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_fourteen")
    doping.dope_surface(nmos_base_copy, "n")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_fifteen")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_sixteen")
    doping.drive_in(nmos_base_copy)
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_seventeen")

    pattern5 = misc_utils.get_fraction_of_pattern(pattern, 4, [0], True)
    nmos_base_copy.deposit_layer("al", 10)  # otherwise it looks bad
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_eighteen")
    lithography.gen_photolithography(
        nmos_base_copy,
        pattern5,
        "novolac_resist",
        f"{item_name}.step_eighteen",
        f"{item_name}.step_nineteen",
    )
    nmos_base_copy.remove_layer("al")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty")
    nmos_base_copy.remove_layer("novolac_resist")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_one")
    nmos_base_copy.grow_layer("al2o3", 100, "al")
    misc_utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_two")


def gen_all():
    nmos_base = Wafer(32, 32, "slight_doped_p_si")
    nmos_base.deposit_layer("si3n4", 20000)
    misc_utils.save_img(nmos_base, "nmos.step_one")
    nmos_base.deposit_layer("novolac_resist", 10000)
    misc_utils.save_img(nmos_base, "nmos.step_one.coated")
    gen_nmos_textures("nmos_cpu", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_sram", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_uart", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_mask_rom", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_bus_controller", copy.deepcopy(nmos_base))
    gen_nmos_dram(copy.deepcopy(nmos_base))


if __name__ == "__main__":
    gen_all()
