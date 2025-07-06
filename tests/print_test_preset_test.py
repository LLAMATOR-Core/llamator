#!/usr/bin/env python3
"""
Console utility that prints example configurations for every available LLAMATOR
preset with clear visual separation.
"""
from __future__ import annotations

from typing import List

# ANSI colors
BRIGHT_CYAN: str = "\033[96m"
RESET: str = "\033[0m"

SEPARATOR_WIDTH: int = 80
SEPARATOR: str = "=" * SEPARATOR_WIDTH


def _print_header(title: str) -> None:
    """Print a colored header centered within a separator line."""
    padding_total = SEPARATOR_WIDTH - len(title) - 2
    left_pad = padding_total // 2
    right_pad = padding_total - left_pad
    print(SEPARATOR)
    print(f"{BRIGHT_CYAN}{' ' * left_pad} {title} {' ' * right_pad}{RESET}")
    print(SEPARATOR)


def display_all_presets() -> None:
    """Iterate over presets and call :func:`print_test_preset` for each one."""
    from llamator.utils.test_presets import preset_configs, print_test_preset

    names: list[str] = sorted(preset_configs)
    for idx, name in enumerate(names):
        _print_header(f"PRESET: {name}")
        print_test_preset(name)
        if idx != len(names) - 1:
            print("\n")  # blank line between presets


if __name__ == "__main__":
    display_all_presets()
