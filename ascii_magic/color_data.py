from dataclasses import dataclass


@dataclass
class ColorData:
    brightness: float
    color: tuple[int, int, int] = (0, 0, 0)
