from __future__ import annotations

from typing import List

COLOR_CODES = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "reset": "\033[0m",
}

BANNER_LINES = [
    " __      __   _    _   _____",
    " \\ \\    / /__| |__| | / ____|",
    "  \\ \\  / / _ \\  _  | | (___  ",
    "   \\ / /  __/ | | |  \\___ \\ ",
    "    \\__/ \\___|_| |_|  ____) |",
    "                   |_____/ ",
]

class AsciiArt:
    def __init__(self, text: str) -> None:
        self.text = text

    def render(self) -> str:
        return "\n".join(BANNER_LINES)


def color_text(text: str, color: str = "white") -> str:
    code = COLOR_CODES.get(color, COLOR_CODES["white"])
    return f"{code}{text}{COLOR_CODES['reset']}"


def rainbow(text: str) -> str:
    colors = [COLOR_CODES["red"], COLOR_CODES["yellow"], COLOR_CODES["green"], COLOR_CODES["cyan"], COLOR_CODES["blue"], COLOR_CODES["magenta"]]
    parts: List[str] = []
    for index, char in enumerate(text):
        if char.strip():
            parts.append(f"{colors[index % len(colors)]}{char}")
        else:
            parts.append(char)
    return "".join(parts) + COLOR_CODES["reset"]
