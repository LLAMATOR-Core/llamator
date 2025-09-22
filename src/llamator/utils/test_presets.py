"""
Dynamic preset generator for ``basic_tests`` and user-facing helpers.

Preset mapping
--------------
all      – every registered attack
rus      – attacks tagged ``lang:ru`` or ``lang:any`` (force ``language='ru'``)
eng      – attacks tagged ``lang:en`` or ``lang:any`` (force ``language='en'``)
vlm     – attacks tagged ``model:vlm``
llm      – attacks tagged ``model:llm``
owasp:*  – one preset per distinct OWASP tag, e.g. ``owasp:llm01``

Public API
----------
* ``preset_configs`` – dict[preset_name, list[(code_name, params)]].
* ``get_test_preset``   – build example code block for a preset.
* ``print_test_preset`` – print that block nicely.
"""

from __future__ import annotations

import copy
import textwrap
from typing import Any, Literal, Tuple

from llamator.attack_provider.attack_registry import test_classes

from .attack_params import format_param_block, get_attack_params

__all__: list[str] = ["get_test_preset", "print_test_preset", "preset_configs"]


# --------------------------------------------------------------------------- #
# internal helpers
# --------------------------------------------------------------------------- #
def _override_language(params: dict[str, Any], lang: str) -> dict[str, Any]:
    """Return a copy of *params* with ``language`` set to *lang* if present."""
    if "language" in params:
        new_params = dict(params)
        new_params["language"] = lang
        return new_params
    return params


def _add(
    mapping: dict[str, list[tuple[str, dict[str, Any]]]],
    key: str,
    code: str,
    params: dict[str, Any],
) -> None:
    """Append ``(code, params)`` to ``mapping[key]`` creating the list if needed."""
    mapping.setdefault(key, []).append((code, params))


def _build_presets() -> dict[str, list[tuple[str, dict[str, Any]]]]:
    """Scan all registered attacks and build the preset mapping."""
    presets: dict[str, list[tuple[str, dict[str, Any]]]] = {
        "all": [],
        "rus": [],
        "eng": [],
        "vlm": [],
        "llm": [],
    }

    for cls in test_classes:
        info: dict[str, Any] = getattr(cls, "info", {})
        code: str = info.get("code_name", cls.__name__)
        tags: list[str] = info.get("tags", [])
        params: dict[str, Any] = get_attack_params(cls)

        _add(presets, "all", code, params)

        if any(tag in {"lang:ru", "lang:any"} for tag in tags):
            _add(presets, "rus", code, _override_language(params, "ru"))
        if any(tag in {"lang:en", "lang:any"} for tag in tags):
            _add(presets, "eng", code, _override_language(params, "en"))

        if "model:vlm" in tags:
            _add(presets, "vlm", code, params)
        if "model:llm" in tags:
            _add(presets, "llm", code, params)

        for tag in tags:
            if tag.startswith("owasp:"):
                _add(presets, tag, code, params)

    return presets


# --------------------------------------------------------------------------- #
# presets built at import time
# --------------------------------------------------------------------------- #
preset_configs: dict[str, list[tuple[str, dict[str, Any]]]] = _build_presets()

# Literal type with all valid preset names (for static type-checkers)
PresetName = Literal[Tuple[Literal[tuple(preset_configs.keys())]]]  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# high-level helpers
# --------------------------------------------------------------------------- #
def get_string_test_preset(preset_name: PresetName = "all") -> str:  # type: ignore[valid-type]
    """
    Build an example ``basic_tests`` code block for *preset_name*.
    """
    preset = preset_configs.get(preset_name)
    if preset is None:
        available = ", ".join(sorted(preset_configs))
        return f"# Preset '{preset_name}' not found. Available presets: {available}."

    lines: list[str] = ["basic_tests = ["]
    for code_name, param_dict in preset:
        lines.append(f'    ("{code_name}", {format_param_block(param_dict)}),')
    lines.append("]")
    return "\n".join(lines)


def get_test_preset(preset_name: PresetName = "all") -> list[tuple[str, dict[str, Any]]]:  # type: ignore[valid-type]
    """
    Return a Python list of ``(code_name, params)`` pairs for *preset_name*.

    Notes
    -----
    * The returned structure is a deep copy of the internal preset to prevent
      accidental mutation of module-level state by callers.
    * Raises ``ValueError`` if the preset does not exist.
    """
    preset = preset_configs.get(preset_name)
    if preset is None:
        available = ", ".join(sorted(preset_configs))
        raise ValueError(f"Unknown preset '{preset_name}'. Available presets: {available}.")
    return [(code, copy.deepcopy(params)) for code, params in preset]


def print_test_preset(preset_name: PresetName = "all") -> None:  # type: ignore[valid-type]
    """Print example block produced by :func:`get_string_test_preset`."""
    print(f"# Example configuration for preset '{preset_name}':")
    print(textwrap.indent(get_string_test_preset(preset_name), "", lambda _l: True))
