# File: llamator/src/llamator/utils/params_example.py
import inspect
from typing import Dict, Literal

from ..attack_provider.attack_registry import test_classes
from .test_presets import preset_configs


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
        params_dict = {}
        for param_name, param_obj in sig.parameters.items():
            if param_name in ("self", "args", "kwargs"):
                continue
            if param_obj.default is inspect.Parameter.empty:
                params_dict[param_name] = "<no default>"
            else:
                params_dict[param_name] = repr(param_obj.default)
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
        params_dict = {}
        for param_name, param_obj in sig.parameters.items():
            if param_name in excluded_params:
                continue
            if param_obj.default is inspect.Parameter.empty:
                params_dict[param_name] = "<no default>"
            else:
                params_dict[param_name] = repr(param_obj.default)
        return params_dict
    except (OSError, TypeError):
        return {}


def get_basic_tests_params_example() -> str:
    """
    Generate example code for configuring basic_tests_params with all available tests
    and their configurable parameters.

    Returns
    -------
    str
        A code snippet showing how to configure basic_tests_params.
    """
    test_configs = []
    sorted_test_classes = sorted(
        test_classes, key=lambda cls: cls.info["name"] if hasattr(cls, "info") else cls.__name__
    )
    for test_cls in sorted_test_classes:
        if hasattr(test_cls, "info") and "code_name" in test_cls.info:
            code_name = test_cls.info["code_name"]
            params = _get_attack_params(test_cls)
            if params:
                param_str = ", ".join([f'"{k}": {v}' for k, v in params.items()])
                test_configs.append(f'    ("{code_name}", {{{param_str}}}),')
            else:
                test_configs.append(f'    ("{code_name}", {{}}),')
    example = "basic_tests_params = [\n" + "\n".join(test_configs) + "\n]"
    return example


def get_preset_tests_params_example(preset_name: Literal["all", "standard"] = "all") -> str:
    """
    Generate example code for configuring basic_tests_params based on a preset configuration.
    If preset_name is "all", returns configuration for all tests (as in get_basic_tests_params_example).

    Parameters
    ----------
    preset_name : Literal["all", "standard"]
        The name of the preset configuration to use.

    Returns
    -------
    str
        A code snippet showing the configuration for the given preset.
    """
    if preset_name.lower() == "all":
        return get_basic_tests_params_example()
    preset = preset_configs.get(preset_name)
    if preset is None:
        return f"# Preset '{preset_name}' not found. Allowed presets: 'all', 'standard'."
    preset_lines = []
    for code_name, params in preset:
        if params:
            params_items = ", ".join([f'"{k}": {v}' for k, v in params.items()])
            preset_lines.append(f'    ("{code_name}", {{{params_items}}}),')
        else:
            preset_lines.append(f'    ("{code_name}", {{}}),')
    example = "basic_tests_params = [\n" + "\n".join(preset_lines) + "\n]"
    return example


def print_preset_tests_params_example(preset_name: Literal["all", "standard"]) -> None:
    """
    Print an example configuration for basic_tests_params based on a preset to the console.
    If preset_name is "all", prints configuration for all tests.

    Parameters
    ----------
    preset_name : Literal["all", "standard"]
        The name of the preset configuration to print.
    """
    example = get_preset_tests_params_example(preset_name)
    print(f"# Example configuration for preset '{preset_name}':")
    print(example)
