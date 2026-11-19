from texture import Wafer, root_path
from PIL import Image
from utils import lithography, doping, mechanicals, misc_utils
import copy

number_table = [
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]


def generateBEOL(
    wafer: Wafer,
    mask: Image.Image,
    total_photolitho_steps: int,
    start_step: int,
    name: str,
    resist: str,
    starter: str,
    beol_step: int,
    iterations: int,
    start_thickness: int,
    split: bool = False,
):
    for i in range(1, iterations + 1):
        beol_name = beol_step + i - 1
        pref = name + ".beol_" + number_table[beol_name]

        if split and i == 1:
            lithography.gen_split_lithography(
                wafer,
                misc_utils.get_fraction_of_pattern(
                    mask, total_photolitho_steps, [start_step + i - 1, start_step + i]
                ),
                resist,
                pref + ".step_one",
                pref + ".step_two",
            )
        else:
            wafer.deposit_layer("silicon_oxycarbide_hydride", 100)
            misc_utils.save_img(wafer, pref + ".step_one")
            lithography.gen_photolithography(
                wafer,
                misc_utils.get_fraction_of_pattern(
                    mask, total_photolitho_steps, [start_step + i - 1, start_step + i]
                ),
                resist,
                pref + ".step_one",
                pref + ".step_two",
            )
        wafer.remove_layer("silicon_oxycarbide_hydride")
        misc_utils.save_img(wafer, pref + ".step_three")
        if resist.endswith("_trilayer"):
            lithography.gen_soc_stripping(
                wafer, resist, pref + ".step_three", pref + ".step_four"
            )
        else:
            wafer.remove_layer(resist)
            misc_utils.save_img(wafer, pref + ".step_four")

        wafer.deposit_layer("tantalum_nitride", 10)
        misc_utils.save_img(wafer, pref + ".step_five")
        wafer.deposit_layer("tantalum", 5)
        misc_utils.save_img(wafer, pref + ".step_six")
        wafer.deposit_layer("copper", 5)
        misc_utils.save_img(wafer, pref + ".step_seven")

        mechanicals.gen_cmp_thickness(
            wafer, pref + ".step_eight", start_thickness + 20 * beol_step + i - 1
        )


def melt_solder(wafer: Wafer):
    for row in range(wafer.base_tex.h):
        for px in range(wafer.base_tex.w):
            if wafer.base_tex.mats[row][px][0] == "tin":
                wafer.base_tex.thicknesses[row][px][0] *= 3
            if wafer.exposed_tex.mats[row][px][0] == "tin":
                wafer.base_tex.thicknesses[row][px][0] *= 3


def gen_packaging(
    wafer: Wafer,
    mask: Image.Image,
    total_photolitho_steps: int,
    start_step: int,
    component_name: str,
    start_name,
):
    pref = component_name + ".pkg."

    wafer.deposit_layer("sio2", 800)
    misc_utils.save_img(wafer, pref + "step_one")
    wafer.deposit_layer("si3n4", 800)
    misc_utils.save_img(wafer, pref + "step_two")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(
            mask, total_photolitho_steps, [start_step], True
        ),
        "novolac_resist",
        pref + "step_two",
        pref + "step_three",
    )
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, pref + "step_four")
    wafer.remove_layer("sio2")
    misc_utils.save_img(wafer, pref + "step_five")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, pref + "step_six")
    wafer.deposit_layer("chromium", 10)
    misc_utils.save_img(wafer, pref + "step_seven")

    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(
            mask, total_photolitho_steps, [start_step + 1]
        ),
        "novolac_resist",
        pref + "step_seven",
        pref + "step_eight",
    )

    wafer.grow_layer("copper", 100, ["novolac_resist"], True)
    misc_utils.save_img(wafer, pref + "step_nine")
    wafer.grow_layer("tin", 1000, ["novolac_resist"], True)
    misc_utils.save_img(wafer, pref + "step_ten")
    wafer.remove_layer("novolac_resist")
    misc_utils.save_img(wafer, pref + "step_eleven")
    melt_solder(wafer)
    misc_utils.save_img(wafer, pref + "step_twelve")
    mechanicals.gen_backgrinding(wafer, pref + "step_thirteen")


def gen_cmos(name, wafer: Wafer):
    mask_pattern = Image.open(
        root_path + "/resources/images/overlay/" + name + ".png"
    ).convert("RGBA")

    # to the trenches
    lithography.gen_split_lithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 1, [0], True, rounding=True),
        "methacrylate_resist",
        name + ".step_two",
        name + ".step_three",
    )

    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_four")
    wafer.remove_layer("sio2")

    misc_utils.save_img(wafer, name + ".step_five")
    wafer.etch_layer("slight_doped_p_si", 0.99)
    misc_utils.save_img(wafer, name + ".step_six")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_seven")
    wafer.grow_layer("sio2", 2500)
    misc_utils.save_img(wafer, name + ".step_eight")
    wafer.deposit_layer("sio2", 500)
    misc_utils.save_img(wafer, name + ".step_nine")
    mechanicals.gen_cmp_thickness(wafer, name + ".step_ten", 101200)
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_eleven")

    lithography.gen_photolithography(  # nmos wells
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [0, 1, 3, 4]),
        "methacrylate_resist",
        name + ".step_eleven",
        name + ".step_twelve",
    )
    doping.dope_surface(wafer, "p", penetrate=True)
    misc_utils.save_img(wafer, name + ".step_thirteen")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_fourteen")

    lithography.gen_photolithography(  # pmos wells
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [5, 6, 8, 9]),
        "methacrylate_resist",
        name + ".step_fourteen",
        name + ".step_fifteen",
    )
    doping.dope_surface(wafer, "n", penetrate=True)
    misc_utils.save_img(wafer, name + ".step_sixteen")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_seventeen")
    doping.drive_in(wafer)
    misc_utils.save_img(wafer, name + ".step_eighteen")

    # dummy gates
    wafer.remove_layer("sio2")
    misc_utils.save_img(wafer, name + ".step_nineteen")
    wafer.grow_layer("sio2", 500)
    misc_utils.save_img(wafer, name + ".step_twenty")
    wafer.deposit_layer("hfo2", 10)
    misc_utils.save_img(wafer, name + ".step_twenty_one")
    wafer.deposit_layer("si", 100)
    misc_utils.save_img(wafer, name + ".step_twenty_two")
    wafer.deposit_layer("si3n4", 30)
    misc_utils.save_img(wafer, name + ".step_twenty_three")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [2, 7], True),
        "methacrylate_resist_trilayer",
        name + ".step_twenty_three",
        name + ".step_twenty_four",
    )
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_twenty_five")
    wafer.remove_layer("si")
    misc_utils.save_img(wafer, name + ".step_twenty_six")
    wafer.remove_layer("hfo2")
    misc_utils.save_img(wafer, name + ".step_twenty_seven")
    lithography.gen_soc_stripping(
        wafer,
        "methacrylate_resist_trilayer",
        name + ".step_twenty_seven",
        name + ".step_twenty_eight",
    )

    # halos
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [1, 3]),
        "methacrylate_resist",
        name + ".step_twenty_eight",
        name + ".step_twenty_nine",
    )
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, name + ".step_thirty")
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, name + ".step_thirty_one")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_thirty_two")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [6, 8]),
        "methacrylate_resist",
        name + ".step_thirty_three",
        name + ".step_thirty_four",
    )
    doping.dope_surface(wafer, "p")
    misc_utils.save_img(wafer, name + ".step_thirty_five")
    doping.dope_surface(wafer, "n")
    misc_utils.save_img(wafer, name + ".step_thirty_six")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_thirty_seven")

    # SiGe
    wafer.grow_layer("sio2", 1000)
    misc_utils.save_img(wafer, name + ".step_thirty_eight")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [5, 6, 8, 9]),
        "methacrylate_resist",
        name + ".step_thirty_eight",
        name + ".step_thirty_nine",
    )
    wafer.remove_layer("sio2")
    misc_utils.save_img(wafer, name + ".step_forty")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_forty_one")
    wafer.etch_layer_thickness(500)
    misc_utils.save_img(wafer, name + ".step_forty_two")
    wafer.deposit_layer("sige", 100)
    misc_utils.save_img(wafer, name + ".step_forty_three")
    doping.dope_surface(wafer, "p", ["sige"], {"p": "p_doped_sige"})
    misc_utils.save_img(wafer, name + ".step_forty_four")
    doping.drive_in(wafer, ["p_doped_sige"], ["sige"], ["slight_doped_p_sige"])
    misc_utils.save_img(wafer, name + ".step_forty_five")

    # nisi
    wafer.deposit_layer("ni", 10)
    misc_utils.save_img(wafer, name + ".step_forty_six")
    doping.intermetallics(
        wafer,
        "ni",
        [
            "si",
            "p_doped_si",
            "n_doped_si",
            "slight_doped_p_si",
            "slight_doped_n_si",
            "p_doped_si_drive_in",
            "n_doped_si_drive_in",
        ],
        "ni2si",
    )
    misc_utils.save_img(wafer, name + ".step_forty_seven")
    wafer.remove_layer("ni")
    misc_utils.save_img(wafer, name + ".step_forty_eight")
    wafer.replace_layer("ni2si", "nisi", 20)
    misc_utils.save_img(wafer, name + ".step_forty_nine")

    # t-cesl
    wafer.deposit_layer("si3n4", 100)
    misc_utils.save_img(wafer, name + ".step_fifty")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [2, 7]),
        "methacrylate_resist",
        name + ".step_fifty",
        name + ".step_fifty_one",
    )
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_fifty_two")
    wafer.remove_layer("methacrylate_resist")
    misc_utils.save_img(wafer, name + ".step_fifty_three")
    wafer.deposit_layer("sio2", 1000)
    misc_utils.save_img(wafer, name + ".step_fifty_four")

    # gate
    mechanicals.gen_cmp_thickness(wafer, name + ".step_fifty_five", 100640)
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_fifty_six")
    wafer.remove_layer("si")
    misc_utils.save_img(wafer, name + ".step_fifty_seven")
    wafer.deposit_layer("titanium_nitride", 20)
    misc_utils.save_img(wafer, name + ".step_fifty_eight")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [2, 7], True),
        "methacrylate_resist_trilayer",
        name + ".step_fifty_eight",
        name + ".step_fifty_nine",
    )
    wafer.remove_layer("titanium_nitride")
    misc_utils.save_img(wafer, name + ".step_sixty")
    lithography.gen_soc_stripping(
        wafer,
        "methacrylate_resist_trilayer",
        name + ".step_sixty",
        name + ".step_sixty_one",
    )
    lithography.gen_soc_stripping(
        wafer,
        "methacrylate_resist_trilayer",
        name + ".step_sixty_one",
        name + ".step_sixty_two",
    )
    wafer.deposit_layer("alti", 20)
    misc_utils.save_img(wafer, name + ".step_sixty_three")
    wafer.deposit_layer("al", 5)
    misc_utils.save_img(wafer, name + ".step_sixty_four")
    mechanicals.gen_cmp_thickness(wafer, name + ".step_sixty_five", 100535)

    # ild
    wafer.deposit_layer("si3n4", 100)
    misc_utils.save_img(wafer, name + ".step_sixty_six")
    wafer.deposit_layer("phosphosilicate_glass", 100)
    misc_utils.save_img(wafer, name + ".step_sixty_seven")
    lithography.gen_photolithography(
        wafer,
        misc_utils.get_fraction_of_pattern(mask_pattern, 10, [0, 4, 5, 9]),
        "methacrylate_resist_trilayer",
        name + ".step_sixty_seven",
        name + ".step_sixty_eight",
    )
    wafer.remove_layer("phosphosilicate_glass")
    misc_utils.save_img(wafer, name + ".step_sixty_nine")
    wafer.remove_layer("si3n4")
    misc_utils.save_img(wafer, name + ".step_seventy")
    lithography.gen_soc_stripping(
        wafer,
        "methacrylate_resist_trilayer",
        name + ".step_seventy",
        name + ".step_seventy_one",
    )
    wafer.deposit_layer("titanium_nitride", 20)
    misc_utils.save_img(wafer, name + ".step_seventy_two")
    wafer.deposit_layer("tungsten", 10)
    misc_utils.save_img(wafer, name + ".step_seventy_three")
    mechanicals.gen_cmp_thickness(
        wafer, name + ".step_seventy_four", 100000 + 500 + 35 + 200
    )

    # beol
    generateBEOL(
        wafer,
        mask_pattern,
        32,
        5,
        name,
        "methacrylate_resist_trilayer",
        name + ".step_seventy_four",
        1,
        3,
        100000 + 500 + 35 + 200,
    )
    generateBEOL(
        wafer,
        mask_pattern,
        17,
        9,
        name,
        "polyhydroxystyrene_resist_trilayer",
        name + ".beol_three.step_eight",
        4,
        3,
        100000 + 500 + 35 + 200 + 60,
    )
    generateBEOL(
        wafer,
        mask_pattern,
        24,
        15,
        name,
        "novolac_resist",
        name + ".beol_six.step_eight",
        7,
        3,
        100000 + 500 + 35 + 200 + 120,
    )

    gen_packaging(wafer, mask_pattern, 29, 3, name, name + ".beol_nine.step_eight")


def gen_all():
    wafer = Wafer(32, 32, "slight_doped_p_si")
    wafer.grow_layer("sio2", 200)
    misc_utils.save_img(wafer, "cmos_base.step_one")
    wafer.deposit_layer("si3n4", 1000)
    misc_utils.save_img(wafer, "cmos_base.step_two")
    wafer.deposit_layer("methacrylate_resist", 1000)
    misc_utils.save_img(wafer, "cmos_base.step_two.coated")

    gen_cmos("cmos_cpu", copy.deepcopy(wafer))
    gen_cmos("cmos_gpu", copy.deepcopy(wafer))
    gen_cmos("cmos_chipset", copy.deepcopy(wafer))
    gen_cmos("cmos_phy", copy.deepcopy(wafer))


if __name__ == "__main__":
    gen_all()
