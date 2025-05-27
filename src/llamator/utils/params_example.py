from __future__ import annotations

import inspect
import textwrap
from typing import Any, Dict, Literal

from ..attack_provider.attack_registry import test_classes
from .test_presets import preset_configs


# --------------------------------------------------------------------------- #
# ---------------------------  LOW-LEVEL RENDERERS -------------------------- #
# --------------------------------------------------------------------------- #
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


def _format_param_block(param_dict: Dict[str, Any], max_line: int = 80, indent: int = 8) -> str:
    """
    Format *param_dict* as a compact or multi-line Python dict literal.
    """
    if not param_dict:
        return "{}"

    items = [f'{_render_py_literal(k)}: {_render_py_literal(param_dict[k])}' for k in sorted(param_dict)]
    one_liner = "{ " + ", ".join(items) + " }"
    if len(one_liner) <= max_line - indent:
        return one_liner

    inner = ",\n".join(" " * indent + item for item in items)
    return "{\n" + inner + "\n" + " " * (indent - 4) + "}"


# --------------------------------------------------------------------------- #
# ------------------------  INTROSPECTION HELPERS --------------------------- #
# --------------------------------------------------------------------------- #
def _get_class_init_params(cls) -> Dict[str, str]:
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
        params_dict: Dict[str, Any] = {}
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


def _get_attack_params(cls) -> Dict[str, str]:
    """
    Extracts initialization parameters from a class's __init__ method
    but excludes the parameters commonly used for configuration in TestBase:
    'self', 'args', 'kwargs', 'client_config', 'attack_config', 'judge_config',
    'artifacts_path'.

    Parameters
    ----------
    cls : type
        The class to inspect.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping parameter names to their default values as strings,
        excluding the parameters above. If a parameter has no default value,
        it is represented by "<no default>".
    """
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
        params_dict: Dict[str, Any] = {}
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


# --------------------------------------------------------------------------- #
# ------------------------  PUBLIC API – GENERATORS ------------------------- #
# --------------------------------------------------------------------------- #
def get_basic_tests_params_example() -> str:
    """
    Build example code block with all registered tests.
    """
    lines = ["basic_tests_params = ["]
    for cls in sorted(test_classes, key=lambda c: c.info.get("name", c.__name__)):
        code_name = cls.info.get("code_name", cls.__name__)
        params = _get_attack_params(cls)
        block = _format_param_block(params)
        lines.append(f'    ("{code_name}", {block}),')
    lines.append("]")
    return "\n".join(lines)


def get_preset_tests_params_example(preset_name: Literal["all", "standard"] = "all") -> str:
    """
    Build example for a named preset or all tests if ``preset_name == "all"``.
    """
    if preset_name.lower() == "all":
        return get_basic_tests_params_example()

    preset = preset_configs.get(preset_name)
    if preset is None:
        return f"# Preset '{preset_name}' not found. Allowed presets: {', '.join(preset_configs)}."

    lines = ["basic_tests_params = ["]
    for code_name, param_dict in preset:
        block = _format_param_block(param_dict)
        lines.append(f'    ("{code_name}", {block}),')
    lines.append("]")
    return "\n".join(lines)


def print_preset_tests_params_example(preset_name: Literal["all", "standard"]) -> None:
    """
    Print example code to stdout.
    """
    example = get_preset_tests_params_example(preset_name)
    print(f"# Example configuration for preset '{preset_name}':")
    print(textwrap.indent(example, "", lambda _l: True))