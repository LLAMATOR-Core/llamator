"""
Печатает логотип LLAMATOR с цветным градиентом.
"""

import colorama
from colorama import Style, Fore, init
from .draw_utils import get_top_border, get_bottom_border, get_empty_line, format_box_line, strip_ansi
from ..__version__ import __version__

init()

def print_logo(box_width: int = 60) -> None:
    """
    Печатает логотип LLAMATOR с цветным градиентом.
    Параметр box_width задаёт минимальную ширину рамки.
    """
    logo_raw = r"""
    __    __    ___    __  ______  __________  ____
   / /   / /   /   |  /  |/  /   |/_  __/ __ \/ __ \
  / /   / /   / /| | / /|_/ / /| | / / / / / / /_/ /
 / /___/ /___/ ___ |/ /  / / ___ |/ / / /_/ / _, _/
/_____/_____/_/  |_/_/  /_/_/  |_/_/  \____/_/ |_|
"""
    logo_lines = logo_raw.strip("\n").split("\n")
    version_line = f"{Style.DIM}v{__version__}{Style.RESET_ALL}"
    # Вычисляем ширину, исходя из содержимого
    inner_content_max = max(
        max(len(strip_ansi(line)) for line in logo_lines),
        len(f"v{__version__}")
    )
    calculated_width = inner_content_max + 4
    # Используем большую ширину: либо заданную, либо вычисленную
    final_box_width = max(box_width, calculated_width)
    print("\n" + get_top_border(final_box_width))
    for line in logo_lines:
        print(format_box_line(line, final_box_width))
    print(get_empty_line(final_box_width))
    inner_width = final_box_width - 4
    version_padding = inner_width - len(f"v{__version__}")
    version_line_formatted = f"{' ' * version_padding}{version_line}"
    print(format_box_line(version_line_formatted, final_box_width))
    print(get_bottom_border(final_box_width))
    print()