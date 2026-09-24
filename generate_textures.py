from PIL import Image

wafer = Image.open("./images/wafer.silicon.png").convert("RGBA")
coating_overlay = Image.open("./images/overlay/wafer_coating.png").convert("RGBA")


class tint:
    def __init__(
        self,
        color: tuple[int, int, int],
        opacity_multiplier: float = 1,
        alt_color: tuple[int, int, int] | None = None,
    ):
        self.color = color
        self.opacity_multiplier = opacity_multiplier
        self.alt_color = alt_color


COLOR_DICT = {
    "novolacs_resist": tint((0xBF, 0xA2, 0x6F), 2.5, (0xDF, 0xD1, 0xB7)),
    "silicon_nitride": tint((0x59, 0x5D, 0x5A), 2.5),
}


def tint_coating(tint: tint):
    img_copy = coating_overlay.copy()
    tmp = img_copy.load()
    assert tmp != None
    w, h = img_copy.size
    for i in range(w):
        for j in range(h):
            tmp[i, j] = (
                tint.color[0],
                tint.color[1],
                tint.color[2],
                int(tmp[i, j][3] * tint.opacity_multiplier),
            )
    return img_copy


class overlayed_image:
    def __init__(self, base_image: Image.Image):
        self.base_image = base_image
        self.stacked_layers = []
        self.tints = []

    def add_layer(self, tint_color: tint):
        self.stacked_layers.append(tint_coating(tint_color))
        self.tints.append(tint_color)

    def remove_top_layer(self):
        self.stacked_layers.pop()

    def composite(self):
        tmp = self.base_image.copy()
        for layer in self.stacked_layers:
            tmp = Image.alpha_composite(tmp, layer)
        return tmp

    def modify_mask(self, mask: Image.Image, layer_num: int = -1):
        self.stacked_layers[layer_num] = self._subtract_mask(
            self.stacked_layers[layer_num], mask, self.tints[layer_num].alt_color
        )

    def subtract_mask(self, mask, layer_num):
        self.stacked_layers[layer_num] = tint_coating(self.tints[layer_num])
        self.stacked_layers[layer_num] = self._subtract_mask(
            self.stacked_layers[layer_num], mask
        )

    def _subtract_mask(
        self,
        image: Image.Image,
        mask: Image.Image,
        alt_color: tuple[int, int, int] | None = None,
    ):
        img_copy = image.copy()
        tmp = img_copy.load()
        mask = mask.convert("RGBA")
        mask_copy = mask.copy()
        mask_tmp = mask_copy.load()
        assert tmp != None
        assert mask_tmp != None

        w, h = img_copy.size
        for i in range(w):
            for j in range(h):
                tmp[i, j] = (
                    tmp[i, j][0],
                    tmp[i, j][1],
                    tmp[i, j][2],
                    int(tmp[i, j][3] * (1 - mask_tmp[i, j][3] / 255)),
                )
                if alt_color:
                    mask_tmp[i, j] = (
                        alt_color[0],
                        alt_color[1],
                        alt_color[2],
                        mask_tmp[i, j][3],
                    )
        if alt_color:
            return Image.alpha_composite(img_copy, mask_copy)
        return img_copy


nmos = overlayed_image(wafer)
out_prefix = "./generated/"

nmos.add_layer(COLOR_DICT["silicon_nitride"])
nmos.composite().save(out_prefix + "wafer.nmos.step_one.png")
nmos.add_layer(COLOR_DICT["novolacs_resist"])
nmos.composite().save(out_prefix + "wafer.nmos.step_one.coated.png")


def generateNMOSProcess(component_name: String):
    mask = Image.open(f"./images/overlay/{component_name}.png")
    nmos.modify_mask(mask)
    nmos.composite().show()
    nmos.composite().save(out_prefix + f"wafer.{component_name}.exposed.png")
    nmos.subtract_mask(mask, -1)
    nmos.composite().show()


generateNMOSProcess("nmos_cpu")
