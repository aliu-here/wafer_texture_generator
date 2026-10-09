from texture import Texture, root_path
from PIL import Image
import time


def gen_nmos_textures(item_name):
    pattern = Image.open(
        root_path + "/resources/images/overlay/" + item_name + ".png"
    ).convert("L")


def gen_all():
    nmos_base = Texture()
    nmos_base.render().show()
    nmos_base.deposit_layer("Si3N4", 20000)
    time.sleep(1)
    nmos_base.render().show()
    nmos_base.deposit_layer("novolac_resist", 100)
    time.sleep(1)
    nmos_base.render().show()


if __name__ == "__main__":
    gen_all()
