"""
Печатает логотип LLAMATOR с цветным градиентом.
"""

import colorama
from colorama import Style, Fore, init
from .draw_utils import get_top_border, get_bottom_border, get_empty_line, format_box_line, strip_ansi
from ..__version__ import __version__

init()

def print_logo() -> None:
    """
    Prints a colorful LLAMATOR logo to the console.
    """
    # Новый логотип согласно заданию
    logo_raw = r"""
    __    __    ___    __  ______  __________  ____
   / /   / /   /   |  /  |/  /   |/_  __/ __ \/ __ \
  / /   / /   / /| | / /|_/ / /| | / / / / / / /_/ /
 / /___/ /___/ ___ |/ /  / / ___ |/ / / /_/ / _, _/
/_____/_____/_/  |_/_/  /_/_/  |_/_/  \____/_/ |_|
"""
    logo_lines = logo_raw.strip("\n").split("\n")
    # Version tag теперь берется из __version__.py
    version_line = f"{Style.DIM}v{__version__}{Style.RESET_ALL}"
    # Вычисляем максимальную длину строки без ANSI кодов
    inner_content_max = max(max(len(strip_ansi(line)) for line in logo_lines), len(f"v{__version__}"))
    # Общая ширина рамки = максимальная длина + 4 (по 1 пробелу слева и справа и границы)
    box_width = inner_content_max + 4
    print("\n" + get_top_border(box_width))
    for line in logo_lines:
        print(format_box_line(line, box_width))
    print(get_empty_line(box_width))
    # Выравнивание версии по правому краю
    inner_width = box_width - 4
    version_padding = inner_width - len(f"v{__version__}")
    version_line_formatted = f"{' ' * version_padding}{version_line}"
    print(format_box_line(version_line_formatted, box_width))
    print(get_bottom_border(box_width))
    print()