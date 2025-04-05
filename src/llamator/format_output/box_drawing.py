# llamator/src/llamator/format_output/box_drawing.py

"""
Этот модуль содержит функции для отрисовки рамок и форматирования строк внутри них.
"""

import re

from .color_consts import BLUE, BRIGHT, RESET


def strip_ansi(text: str) -> str:
    """
    Remove ANSI escape sequences from text.
    """
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    return ansi_escape.sub("", text)


def get_top_border(box_width: int) -> str:
    """
    Returns the top border string of a box with given total width (including borders).
    """
    return f"{BLUE + BRIGHT}╔{'═' * (box_width - 2)}╗{RESET}"


def get_bottom_border(box_width: int) -> str:
    """
    Returns the bottom border string of a box with given total width (including borders).
    """
    return f"{BLUE + BRIGHT}╚{'═' * (box_width - 2)}╝{RESET}"


def get_empty_line(box_width: int) -> str:
    """
    Returns an empty line with borders for a box with given total width.
    """
    return f"{BLUE + BRIGHT}║{' ' * (box_width - 2)}║{RESET}"


def get_separator_line(box_width: int) -> str:
    """
    Returns a separator line within a box with given total width.
    """
    return f"{BLUE + BRIGHT}╠{'═' * (box_width - 2)}╣{RESET}"


def format_box_line(content: str, box_width: int) -> str:
    """
    Returns a formatted line within a box with given total width.
    Внутреннее пространство для текста: box_width - 4 символа.
    """
    inner_width = box_width - 4
    content_stripped = strip_ansi(content)
    if len(content_stripped) > inner_width:
        content_stripped = content_stripped[:inner_width]
        content = content_stripped
    padding = inner_width - len(content_stripped)
    return f"{BLUE + BRIGHT}║{RESET} {content}{' ' * padding} {BLUE + BRIGHT}║{RESET}"


def format_centered_line(text: str, box_width: int) -> str:
    """
    Returns a formatted centered line within a box with given total width.
    Внутреннее пространство для текста: box_width - 4 символа.
    """
    inner_width = box_width - 4
    text_stripped = strip_ansi(text)
    if len(text_stripped) > inner_width:
        text_stripped = text_stripped[:inner_width]
    left_padding = (inner_width - len(text_stripped)) // 2
    right_padding = inner_width - len(text_stripped) - left_padding
    return f"{BLUE + BRIGHT}║{RESET} {' ' * left_padding}{text_stripped}{' ' * right_padding} {BLUE + BRIGHT}║{RESET}"


def print_box(content_lines: list, box_width: int) -> None:
    """
    Prints a box with given content lines and total width.
    """
    print(get_top_border(box_width))
    for line in content_lines:
        print(format_box_line(line, box_width))
    print(get_bottom_border(box_width))


def print_box_with_header(header: str, content_lines: list, box_width: int) -> None:
    """
    Prints a box with a header and content lines with even borders.
    """
    visible_header = strip_ansi(header)
    header_len = len(visible_header)
    inner_width = box_width - 4
    if header_len > inner_width:
        header = visible_header[:inner_width]
        header_len = len(header)
    left_padding = (inner_width - header_len) // 2
    right_padding = inner_width - header_len - left_padding
    print(get_top_border(box_width))
    print(f"{BLUE + BRIGHT}║{RESET} {' ' * left_padding}{header}{' ' * right_padding} {BLUE + BRIGHT}║{RESET}")
    print(get_separator_line(box_width))
    for line in content_lines:
        visible_line = strip_ansi(line)
        if len(visible_line) > inner_width:
            visible_line = visible_line[:inner_width]
            line = visible_line
        padding = inner_width - len(strip_ansi(line))
        print(f"{BLUE + BRIGHT}║{RESET} {line}{' ' * padding} {BLUE + BRIGHT}║{RESET}")
    print(get_bottom_border(box_width))
