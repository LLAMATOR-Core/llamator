# llamator/src/llamator/format_output/color_consts.py

"""
Этот модуль содержит глобальные цветовые константы и стиль для форматирования вывода
с использованием colorama.
"""

import colorama
from colorama import Fore, Style

colorama.init(autoreset=False)

RESET = Style.RESET_ALL
BRIGHT = Style.BRIGHT

BRIGHT_CYAN = Fore.CYAN + Style.BRIGHT
BRIGHT_RED = Fore.RED + Style.BRIGHT
BRIGHT_GREEN = Fore.GREEN + Style.BRIGHT
BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX + Style.BRIGHT

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
LIGHTBLUE = colorama.Fore.LIGHTBLUE_EX
