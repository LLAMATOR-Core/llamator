"""
Dynamic preset generator for ``basic_tests_params`` and user-facing helpers.

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
* ``PresetName``     – ``Literal`` with all available preset names.
* ``get_test_preset``   – build example code block for a preset.
* ``print_test_preset`` – print that block nicely.
"""

from __future__ import annotations

import textwrap
from typing import Any, Dict, List, Literal, Tuple

from llamator.attack_provider.attack_registry import test_classes
from .attack_params import (
    format_param_block,
    get_attack_params,
)

# --------------------------------------------------------------------------- #
# internal helpers
# --------------------------------------------------------------------------- #
def _override_language(params: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Return a copy of *params* with ``language`` set to *lang* if present."""
    if "language" in params:
        new_params = dict(params)
        new_params["language"] = lang
        return new_params
    return params


def _add(
    mapping: Dict[str, List[Tuple[str, Dict[str, Any]]]],
    key: str,
    code: str,
    params: Dict[str, Any],
) -> None:
    """Append ``(code, params)`` to ``mapping[key]`` creating the list if needed."""
    mapping.setdefault(key, []).append((code, params))


def _build_presets() -> Dict[str, List[Tuple[str, Dict[str, Any]]]]:
    """Scan all registered attacks and build the preset mapping."""
    presets: Dict[str, List[Tuple[str, Dict[str, Any]]]] = {
        "all": [],
        "rus": [],
        "eng": [],
        "vlm": [],
        "llm": [],
    }

    for cls in test_classes:
        info: Dict[str, Any] = getattr(cls, "info", {})
        code: str = info.get("code_name", cls.__name__)
        tags: List[str] = info.get("tags", [])
        params: Dict[str, Any] = get_attack_params(cls)

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
preset_configs: Dict[str, List[Tuple[str, Dict[str, Any]]]] = _build_presets()

# Literal type with all valid preset names (for static type-checkers)
PresetName = Literal[Tuple[Literal[tuple(preset_configs.keys())]]]  # type: ignore[misc]

# --------------------------------------------------------------------------- #
# high-level helpers (moved from params_example.py)
# --------------------------------------------------------------------------- #
def _get_all_tests_example() -> str:
    """Return an example block with every registered attack."""
    lines: List[str] = ["basic_tests_params = ["]
    for cls in sorted(test_classes, key=lambda c: c.info.get("name", c.__name__)):
        code_name = cls.info.get("code_name", cls.__name__)
        params = get_attack_params(cls)
        lines.append(f'    ("{code_name}", {format_param_block(params)}),')
    lines.append("]")
    return "\n".join(lines)


def get_test_preset(preset_name: PresetName = "all") -> str:  # type: ignore[valid-type]
    """
    Build an example ``basic_tests_params`` code block for *preset_name*.

    * ``all`` – every registered attack.
    * Any other value must exist in ``preset_configs``.
    """
    if preset_name == "all":
        return _get_all_tests_example()

    preset = preset_configs.get(preset_name)
    if preset is None:
        available = ", ".join(sorted(preset_configs))
        return f"# Preset '{preset_name}' not found. Available presets: {available}."

    lines: List[str] = ["basic_tests_params = ["]
    for code_name, param_dict in preset:
        lines.append(f'    ("{code_name}", {format_param_block(param_dict)}),')
    lines.append("]")
    return "\n".join(lines)


def print_test_preset(preset_name: PresetName = "all") -> None:  # type: ignore[valid-type]
    """Print example block produced by :func:`get_test_preset`."""
    print(f"# Example configuration for preset '{preset_name}':")
    print(textwrap.indent(get_test_preset(preset_name), "", lambda _l: True))


# --------------------------------------------------------------------------- #
# public re-exports
# --------------------------------------------------------------------------- #
__all__: list[str] = [
    "get_test_preset",
    "print_test_preset",
    "preset_configs"
]