from texture import Wafer, root_path
from PIL import Image
import utils
import copy


def gen_nmos_textures(item_name, nmos_base_copy: Wafer):
    pattern = Image.open(
        root_path + "/resources/images/overlay/" + item_name + ".png"
    ).convert("RGBA")

    pattern1 = utils.get_fraction_of_pattern(pattern, 5, 0, True)
    utils.gen_split_lithography(
        nmos_base_copy,
        pattern1,
        "novolac_resist",
        f"{item_name}.step_one",
        f"{item_name}.step_two",
    )
    nmos_base_copy.remove_layer("si3n4")
    utils.save_img(nmos_base_copy, f"{item_name}.step_three")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_four")
    utils.dope_surface(nmos_base_copy, "p", "si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_five")
    nmos_base_copy.grow_layer("sio2", 40000, ["si", "p_doped_si", "n_doped_si"])
    utils.save_img(nmos_base_copy, f"{item_name}.step_six")
    nmos_base_copy.remove_layer("si3n4")
    utils.save_img(nmos_base_copy, f"{item_name}.step_seven")

    pattern2 = utils.get_fraction_of_pattern(pattern, 5, 2)
    utils.gen_photolithography(
        nmos_base_copy,
        pattern2,
        "novolac_resist",
        f"{item_name}.step_seven",
        f"{item_name}.step_eight",
    )
    utils.dope_surface(nmos_base_copy, "n", "si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_nine")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_ten")

    pattern3 = utils.get_fraction_of_pattern(pattern, 5, 1, True)
    nmos_base_copy.grow_layer("sio2", 4000, ["si", "p_doped_si", "n_doped_si"])
    utils.save_img(nmos_base_copy, f"{item_name}.step_eleven")
    nmos_base_copy.deposit_layer("si", 500)
    utils.save_img(nmos_base_copy, f"{item_name}.step_twelve")
    utils.gen_photolithography(
        nmos_base_copy,
        pattern3,
        "novolac_resist",
        f"{item_name}.step_twelve",
        f"{item_name}.step_thirteen",
    )
    nmos_base_copy.remove_layer("si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_fourteen")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_fifteen")

    pattern4 = utils.get_fraction_of_pattern(pattern, 5, 3)
    utils.gen_photolithography(
        nmos_base_copy,
        pattern4,
        "novolac_resist",
        f"{item_name}.step_fifteen",
        f"{item_name}.step_sixteen",
    )
    nmos_base_copy.remove_layer("sio2")
    utils.save_img(nmos_base_copy, f"{item_name}.step_seventeen")
    utils.dope_surface(nmos_base_copy, "n", "si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_eighteen")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_nineteen")
    utils.drive_in(nmos_base_copy)
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty")

    pattern5 = utils.get_fraction_of_pattern(pattern, 5, 4, True, 0.9)
    nmos_base_copy.deposit_layer("al", 5)  # otherwise it looks bad
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_one")
    utils.gen_photolithography(
        nmos_base_copy,
        pattern5,
        "novolac_resist",
        f"{item_name}.step_twenty_one",
        f"{item_name}.step_twenty_two",
    )
    nmos_base_copy.remove_layer("al")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_three")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_four")
    nmos_base_copy.grow_layer("al2o3", 10, "al")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_five")


def gen_nmos_dram(nmos_base_copy: Wafer):  # thanks planetme code organization
    item_name = "nmos_dram"
    pattern = Image.open(
        root_path + "/resources/images/overlay/" + item_name + ".png"
    ).convert("RGBA")

    pattern1 = utils.get_fraction_of_pattern(pattern, 4, 0, True)
    utils.gen_split_lithography(
        nmos_base_copy,
        pattern1,
        "novolac_resist",
        f"{item_name}.step_one",
        f"{item_name}.step_two",
    )
    nmos_base_copy.remove_layer("si3n4")
    utils.save_img(nmos_base_copy, f"{item_name}.step_three")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_four")
    utils.dope_surface(nmos_base_copy, "p", "si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_five")
    nmos_base_copy.grow_layer("sio2", 40000, ["si", "p_doped_si", "n_doped_si"])
    utils.save_img(nmos_base_copy, f"{item_name}.step_six")
    nmos_base_copy.remove_layer("si3n4")
    utils.save_img(nmos_base_copy, f"{item_name}.step_seven")

    pattern3 = utils.get_fraction_of_pattern(pattern, 4, 1, True)
    nmos_base_copy.grow_layer("sio2", 4000, ["si", "p_doped_si", "n_doped_si"])
    utils.save_img(nmos_base_copy, f"{item_name}.step_eleven")
    nmos_base_copy.deposit_layer("si", 500)
    utils.save_img(nmos_base_copy, f"{item_name}.step_twelve")
    utils.gen_photolithography(
        nmos_base_copy,
        pattern3,
        "novolac_resist",
        f"{item_name}.step_twelve",
        f"{item_name}.step_thirteen",
    )
    nmos_base_copy.remove_layer("si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_thirteen")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_fourteen")

    pattern4 = utils.get_fraction_of_pattern(pattern, 4, 3)
    utils.gen_photolithography(
        nmos_base_copy,
        pattern4,
        "novolac_resist",
        f"{item_name}.step_fifteen",
        f"{item_name}.step_sixteen",
    )
    nmos_base_copy.remove_layer("sio2")
    utils.save_img(nmos_base_copy, f"{item_name}.step_fifteen")
    utils.dope_surface(nmos_base_copy, "n", "si")
    utils.save_img(nmos_base_copy, f"{item_name}.step_sixteen")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_seventeen")
    utils.drive_in(nmos_base_copy)
    utils.save_img(nmos_base_copy, f"{item_name}.step_eighteen")

    pattern5 = utils.get_fraction_of_pattern(pattern, 4, 2, True, 0.9)
    nmos_base_copy.deposit_layer("al", 5)  # otherwise it looks bad
    utils.save_img(nmos_base_copy, f"{item_name}.step_nineteen")
    utils.gen_photolithography(
        nmos_base_copy,
        pattern5,
        "novolac_resist",
        f"{item_name}.step_twenty_one",
        f"{item_name}.step_twenty_two",
    )
    nmos_base_copy.remove_layer("al")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty")
    nmos_base_copy.remove_layer("novolac_resist")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_one")
    nmos_base_copy.grow_layer("al2o3", 10, "al")
    utils.save_img(nmos_base_copy, f"{item_name}.step_twenty_two")


def gen_all():
    nmos_base = Wafer(32, 32)
    nmos_base.deposit_layer("si3n4", 20000)
    utils.save_img(nmos_base, "nmos.step_one")
    nmos_base.deposit_layer("novolac_resist", 20000)
    utils.save_img(nmos_base, "nmos.step_one.coated")
    gen_nmos_textures("nmos_cpu", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_sram", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_uart", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_mask_rom", copy.deepcopy(nmos_base))
    gen_nmos_textures("nmos_bus_controller", copy.deepcopy(nmos_base))
    gen_nmos_dram(copy.deepcopy(nmos_base))


if __name__ == "__main__":
    gen_all()
