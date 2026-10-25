from texture import Wafer
from PIL import Image
from utils import save_img


def gen_photolithography(
    texture: Wafer,
    mask: Image.Image,
    photoresist_mat: str,
    input_name,
    output_name,
    thickness=10000,
    mandrel=False,
    liftoff=False,
):
    if photoresist_mat.endswith("trilayer"):
        texture.deposit_layer("spin_on_carbon", 200)
        save_img(texture, input_name + ".hardmasked")
        texture.deposit_layer("silicon_oxynitride", 200)
        save_img(texture, input_name + ".ibarc")
        if mandrel:
            texture.deposit_layer("silicon", 250)
            save_img(texture, input_name + ".mandrel")
        input_name = input_name + ".mandrel" if mandrel else input_name + ".ibarc"
    texture.deposit_layer(photoresist_mat, thickness)
    save_img(texture, input_name + ".coated")
    texture.mod_layer(photoresist_mat, "exposed_" + photoresist_mat, mask)
    save_img(texture, input_name + ".deposited" if liftoff else ".exposed")
    texture.remove_layer("exposed_" + photoresist_mat)
    if photoresist_mat.endswith("trilayer"):
        save_img(texture, input_name + ".developed")
        texture.remove_layer("silicon_oxynitride")
        save_img(texture, input_name + ".etched")
        texture.remove_layer("spin_on_carbon")
        save_img(texture, output_name)
    else:
        save_img(texture, output_name)


def gen_split_lithography(
    texture: Wafer,
    mask: Image.Image,
    photoresist_mat,
    intermediate_name,
    output_name,
):
    texture.mod_layer(photoresist_mat, "exposed_" + photoresist_mat, mask)
    save_img(texture, intermediate_name + ".exposed")
    texture.remove_layer("exposed_" + photoresist_mat)
    save_img(texture, output_name)


def gen_resist_stripping(
    texture: Wafer, input_name, output_name, resist_mat, bombarded, solvent
):
    if not bombarded and solvent:
        texture.remove_layer(resist_mat)
        save_img(texture, output_name)
    intermediate = input_name + ".ashed" if bombarded else output_name
    if not bombarded:
        texture.remove_layer(resist_mat)
        save_img(texture, output_name)
    else:
        texture.replace_layer(resist_mat, "ash", 200)
        save_img(texture, intermediate)
        texture.remove_layer("ash")
        save_img(texture, output_name)


def gen_soc_stripping(texture: Wafer, input_name, output_name):
    texture.replace_layer("spin_on_carbon", "ash", 200)
    save_img(texture, input_name + ".ashed")
    texture.remove_layer("silicon_oxynitride")
    texture.remove_layer("ash")
    save_img(texture, output_name)
