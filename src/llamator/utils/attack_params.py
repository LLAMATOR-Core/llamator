"""
Utility helpers that render Python-literal fragments for LLAMATOR.

This module now provides only low-level helpers:

* ``_render_py_literal`` – stringify values as valid Python literals.
* ``format_param_block`` – pretty-print dicts for config examples.
* ``get_attack_params`` – extract constructor parameters of an attack.
"""

from __future__ import annotations

import inspect
from typing import Any, Dict
from ..attack_provider.attack_registry import test_classes  # noqa: F401

__all__: list[str] = [
    "format_param_block",
    "get_attack_params",
    "get_class_init_params"
]

# ───────────────────────────── low-level renderers ──────────────────────────
def _render_py_literal(value: Any) -> str:
    """
    Convert *value* into a valid Python literal string.
    """
    if isinstance(value, str):
        # Leave literals/sentinels intact (already quoted or <no default>).
        if value.startswith(("'", '"')) or value.startswith("<"):
            return value
        return f'"{value}"'

    if isinstance(value, dict):
        items = ", ".join(f"{_render_py_literal(k)}: {_render_py_literal(v)}" for k, v in value.items())
        return f"{{ {items} }}"

    if isinstance(value, list):
        items = ", ".join(_render_py_literal(v) for v in value)
        return f"[{items}]"

    if isinstance(value, tuple):
        items = ", ".join(_render_py_literal(v) for v in value)
        return f"({items},)" if len(value) == 1 else f"({items})"

    return repr(value)


def format_param_block(param_dict: Dict[str, Any], max_line: int = 80, indent: int = 8) -> str:
    """
    Format *param_dict* as a compact or multi-line Python dict literal.
    """
    if not param_dict:
        return "{}"

    items = [f"{_render_py_literal(k)}: {_render_py_literal(param_dict[k])}" for k in sorted(param_dict)]
    one_liner = "{ " + ", ".join(items) + " }"
    if len(one_liner) <= max_line - indent:
        return one_liner

    inner = ",\n".join(" " * indent + item for item in items)
    return "{\n" + inner + "\n" + " " * (indent - 4) + "}"


# ───────────────────────── introspection helper (shared) ────────────────────
def get_class_init_params(cls) -> dict[str, str]:
    """
    Extracts all initialization parameters from a class's __init__ method,
    excluding 'self', 'args' and 'kwargs'.

    Parameters
    ----------
    cls : type
        The class to inspect.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping parameter names to their default values as strings.
        If a parameter has no default value, it is represented by "<no default>".
    """
    try:
        sig = inspect.signature(cls.__init__)
        params_dict: dict[str, Any] = {}
        for param_name, param_obj in sig.parameters.items():
            if param_name in ("self", "args", "kwargs"):
                continue
            if param_obj.default is inspect.Parameter.empty:
                params_dict[param_name] = "<no default>"
            else:
                params_dict[param_name] = param_obj.default
        return params_dict
    except (OSError, TypeError):
        return {}

def get_attack_params(cls) -> Dict[str, Any]:
    """Return constructor parameters for *cls* excluding TestBase-specific args."""
    excluded = {
        "self",
        "args",
        "kwargs",
        "client_config",
        "attack_config",
        "judge_config",
        "artifacts_path",
    }
    try:
        excluded_params = {
            "self",
            "args",
            "kwargs",
            "client_config",
            "attack_config",
            "judge_config",
            "artifacts_path",
        }
        sig = inspect.signature(cls.__init__)
        params_dict: dict[str, Any] = {}
        for param_name, param_obj in sig.parameters.items():
            if param_name in excluded_params:
                continue
            if param_obj.default is inspect.Parameter.empty:
                params_dict[param_name] = "<no default>"
            else:
                params_dict[param_name] = param_obj.default
        return params_dict
    except (OSError, TypeError):
        return {}