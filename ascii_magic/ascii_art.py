__version__ = '2.7.5'

from ascii_magic.color_data import ColorData
from ascii_magic.constants import (
    ColorMode,
    Front,
    Back,
    CHARS_BY_DENSITY,
    PALETTE,
    PILLOW_VERSION,
)

from PIL import Image

import typing as t


class AsciiArt:
    __VERSION__ = __version__
    __PILLOW_VERSION__ = PILLOW_VERSION
    _image: Image.Image

    def __init__(self, image: Image.Image):
        self._image = image

    @property
    def image(self) -> Image.Image:
        return self._image

    @image.setter
    def image(self, value: Image.Image):
        self._image = value

    def to_terminal(
        self,
        columns: int = 120,
        width_ratio: float = 2.2,
        chars: str = CHARS_BY_DENSITY,
        color_mode: ColorMode = ColorMode.ANSI_16_COLOR,
        back: "t.Optional[Back]" = None,
        front: "t.Optional[Front]" = None,
    ):
        lines = self._img_to_art(
            columns=columns,
            width_ratio=width_ratio,
        )

        return '\n'.join(
            self.get_esc_seq(back) +
            ''.join(
                self.render_character(c.brightness, color_mode, c, chars, front) for c in line
            ) +
            self.get_esc_seq(Back.RESET)
            for line in lines
        ) + self.get_esc_seq(Front.RESET)

    def _img_to_art(
        self,
        columns: int = 120,
        width_ratio: float = 2.2,
    ) -> list[list[ColorData]]:
        img_w, img_h = self._image.size
        scalar = img_w * width_ratio / columns
        new_w = int(img_w * width_ratio / scalar)
        new_h = int(img_h / scalar)
        rgb_img = self._image.resize((new_w, new_h)) # pyright: ignore[reportUnknownMemberType]
        color_palette = self._image.getpalette()

        grayscale_img = rgb_img.convert("L")

        lines: list[list[ColorData]] = []
        for h in range(new_h):
            line: list[ColorData] = []
            for w in range(new_w):
                # get brightness value
                brightness = self.get_brightness_value(grayscale_img, w, h)
                pixel = rgb_img.getpixel((w, h))

                # getpixel() may return an int, instead of tuple of ints, if the source img is a PNG with a transparency layer
                if isinstance(pixel, (int, float)):
                    pixel = int(pixel)
                    rgb = (pixel, pixel, pixel) if color_palette is None else (color_palette[pixel * 3], color_palette[pixel * 3 + 1], color_palette[pixel * 3 + 2])
                elif pixel is None:
                    rgb = (0, 0, 0)
                else:
                    rgb = (pixel[0], pixel[1], pixel[2])

                character = ColorData(brightness, rgb)
                line.append(character)
            lines.append(line)
        return lines

    @staticmethod
    def get_brightness_value(img: Image.Image, w: int, h: int) -> float:
        pixel = img.getpixel((w, h))
        if isinstance(pixel, (float, int)):
            return pixel / 255
        elif isinstance(pixel, (list, tuple)) and len(pixel) > 0:
            return float(pixel[0]) / 255
        else:
            return 0

    @staticmethod
    def get_esc_seq(color: Front | Back | tuple[int, int, int] | None) -> str:
        if isinstance(color, tuple):
            return '\033[38;2;{};{};{}m'.format(*color)
        return '\033[' + str(color.value) + 'm' if color else ''

    @staticmethod
    def calculate_color_distance(
        v1: "t.Union[t.List[float], t.Tuple[float, float, float]]",
        v2: "t.Union[t.List[float], t.Tuple[float, float, float]]"
    ) -> float:
        return 0.299 * (v1[0] - v2[0])**2 + 0.587 * (v1[1] - v2[1])**2 + 0.114 * (v1[2] - v2[2])**2

    @classmethod
    def rgb_to_terminal_color(cls, color_data: ColorData) -> Front:
        return min(PALETTE, key=lambda c: cls.calculate_color_distance([v * color_data.brightness * 255 for v in c[0]], color_data.color))[1]

    @staticmethod
    def get_char_by_brightness(brightness: float, chars: str) -> str:
        char_index = int(brightness * (len(chars) - 1))
        return chars[char_index]

    @classmethod
    def render_character(cls, brightness: float, color_mode: ColorMode, color_data: ColorData, chars: str, front: Front | None) -> str:
        char = cls.get_char_by_brightness(brightness, chars)
        match color_mode:
            case ColorMode.MONOCHROME:
                return char if front is None else cls.get_esc_seq(front) + char
            case ColorMode.ANSI_16_COLOR:
                return cls.get_esc_seq(cls.rgb_to_terminal_color(color_data)) + char
            case ColorMode.FULL_COLOR:
                return cls.get_esc_seq(color_data.color) + char
