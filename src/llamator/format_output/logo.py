# llamator/src/llamator/format_output/logo.py

import textwrap

from colorama import init

from ..__version__ import __version__
from .box_drawing import format_box_line, get_bottom_border, get_empty_line, get_top_border, strip_ansi
from .color_consts import BRIGHT, RESET

init()


def print_logo(box_width: int = 60) -> None:
    """
    Печатает логотип с фиксированным выравниванием и центрированной версией.
    """
    logo_raw = r"""
    __    __    ___    __  ______  __________  ____
   / /   / /   /   |  /  |/  /   |/_  __/ __ \/ __ \
  / /   / /   / /| | / /|_/ / /| | / / / / / / /_/ /
 / /___/ /___/ ___ |/ /  / / ___ |/ / / /_/ / _, _/
/_____/_____/_/  |_/_/  /_/_/  |_/_/  \____/_/ |_|
"""
    logo_raw = textwrap.dedent(logo_raw).strip("\n")
    logo_lines = logo_raw.split("\n")

    # Определяем отступ для логотипа
    first_line_clean = strip_ansi(logo_lines[0])
    version_text = f"v{__version__}"
    max_content_width = max(len(first_line_clean), len(version_text))

    # Рассчитываем ширину рамки
    calculated_width = max_content_width + 4
    final_box_width = max(box_width, calculated_width)
    inner_width = final_box_width - 4

    # Фиксированный отступ для логотипа
    logo_padding = (inner_width - len(first_line_clean)) // 2
    logo_padding_str = " " * logo_padding

    print("\n" + get_top_border(final_box_width))
    for line in logo_lines:
        aligned_line = logo_padding_str + line
        print(format_box_line(aligned_line, final_box_width))
    print(get_empty_line(final_box_width))

    # Центрируем версию по всей ширине блока
    version_spaces = (inner_width - len(version_text)) // 2
    version_line = f"{' ' * version_spaces}{BRIGHT}{version_text}{RESET}"
    print(format_box_line(version_line, final_box_width))

    print(get_bottom_border(final_box_width))
    print()
