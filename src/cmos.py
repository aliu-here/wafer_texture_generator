from texture import Wafer, root_path
from PIL import Image
import utils
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
    split: bool = False,
):
    for i in range(iterations):
        input = ""
        beol_name = beol_step + i - 1
        pref = "wafer." + name + ".beol_" + number_table[beol_name - 1]
        if i == 1:
            input = starter
        else:
            input = (
                "wafer." + name + ".beol_" + number_table[beol_name - 1] + ".step_eight"
            )

        if split and i == 1:
            utils.gen_split_lithography(
                wafer,
                utils.get_fraction_of_pattern(mask, total_photolitho_steps, start_step),
                resist,
                pref + ".step_one",
                pref + ".step_two",
            )
        else:
            wafer.deposit_layer("silicon_oxycarbide_hydride", 200)
            utils.save_img(wafer, pref + ".step_one")
            utils.gen_photolithography(
                wafer,
                utils.get_fraction_of_pattern(mask, total_photolitho_steps, start_step),
                resist,
                pref + ".step_one",
                pref + ".step_two",
            )
