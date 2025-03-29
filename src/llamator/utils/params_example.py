# File: llamator/src/llamator/utils/params_example.py
import inspect
import re
from typing import Dict, Literal

from ..attack_provider.attack_registry import test_classes
from .test_presets import preset_configs  # Import preset configurations


def _get_class_init_params(cls) -> Dict[str, str]:
    """
    Extract initialization parameters from a class's __init__ method.

    Parameters
    ----------
    cls : type
        The class to inspect.

    Returns
    -------
    Dict[str, str]
        Dictionary mapping parameter names to their default values as strings.
    """
    try:
        source = inspect.getsource(cls.__init__)
        # Find the parameter list
        param_match = re.search(r"def __init__\s*\(\s*(.*?)\):", source, re.DOTALL)
        if not param_match:
            return {}
        param_text = param_match.group(1)
        # Remove common parameters we don't want to include
        excluded_params = [
            "self",
            "client_config: ClientConfig",
            "attack_config: AttackConfig",
            "judge_config: JudgeConfig",
            "artifacts_path: Optional[str]",
            "*args",
            "**kwargs",
        ]
        for param in excluded_params:
            param_text = param_text.replace(param, "")
        # Extract remaining parameters with defaults
        params = {}
        param_matches = re.finditer(r"(\w+)(?:\s*:\s*[^=]+)?\s*=\s*([^,]+)", param_text)
        for match in param_matches:
            param_name = match.group(1)
            default_value = match.group(2).strip()
            params[param_name] = default_value
        return params
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
    # Sort test classes by name for consistent output
    sorted_test_classes = sorted(
        test_classes, key=lambda cls: cls.info["name"] if hasattr(cls, "info") else cls.__name__
    )
    for test_cls in sorted_test_classes:
        if hasattr(test_cls, "info") and "code_name" in test_cls.info:
            code_name = test_cls.info["code_name"]
            params = _get_class_init_params(test_cls)
            if params:
                # Use proper dictionary syntax: "key": value
                param_str = ", ".join([f'"{k}": {v}' for k, v in params.items()])
                test_configs.append(f'    ("{code_name}", {{{param_str}}}),')
            else:
                test_configs.append(f'    ("{code_name}", {{}}),')
    example = "basic_tests_params = [\n" + "\n".join(test_configs) + "\n]"
    return example


def get_preset_tests_params_example(preset_name: Literal["all", "standard"]) -> str:
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
    # preset_name is "standard"
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
