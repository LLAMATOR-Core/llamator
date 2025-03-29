import colorama

RESET = colorama.Style.RESET_ALL
DIM_WHITE = colorama.Style.DIM + colorama.Fore.WHITE
LIGHT_MAGENTA = colorama.Fore.LIGHTMAGENTA_EX
MAGENTA = colorama.Fore.MAGENTA


def print_logo() -> None:
    logo = r"""
    __    __    ___    __  ______  __________  ____
   / /   / /   /   |  /  |/  /   |/_  __/ __ \/ __ \
  / /   / /   / /| | / /|_/ / /| | / / / / / / /_/ /
 / /___/ /___/ ___ |/ /  / / ___ |/ / / /_/ / _, _/
/_____/_____/_/  |_/_/  /_/_/  |_/_/  \____/_/ |_|
"""
    print(logo)
