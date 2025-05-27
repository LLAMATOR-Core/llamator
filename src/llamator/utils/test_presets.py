"""
This module contains preset configurations for basic_tests_params.
Each preset is a list of tuples, where each tuple consists of a test code name and a dictionary of parameters.
Allowed preset names are "standard" and "all".
"""
preset_configs = {
    "standard": [
        ("suffix", {"custom_dataset": None, "num_attempts": 1}),
        ("aim_jailbreak", {"num_attempts": 1}),
        ("autodan_turbo", {
            "custom_dataset": None,
            "language": "any",
            "multistage_depth": 10,
            "num_attempts": 1,
            "strategy_library_size": 10
        }),
        ("base64_injection", {"custom_dataset": None, "num_attempts": 1}),
        ("bon", {
            "custom_dataset": None,
            "language": "any",
            "num_attempts": 1,
            "num_transformations": 5,
            "sigma": 0.4
        }),
        ("crescendo", {
            "custom_dataset": None,
            "language": "any",
            "multistage_depth": 5,
            "num_attempts": 1
        }),
        ("deceptive_delight", {"custom_dataset": None, "num_attempts": 1}),
        ("dialogue_injection_continuation", {"custom_dataset": None, "language": "any", "num_attempts": 1}),
        ("dialogue_injection_devmode", {"custom_dataset": None, "num_attempts": 1}),
        ("dan", {"language": "any", "num_attempts": 1}),
        ("ethical_compliance", {"custom_dataset": None, "num_attempts": 1}),
        ("harmbench", {"custom_dataset": None, "language": "any", "num_attempts": 1}),
        ("linguistic_evasion", {"num_attempts": 1}),
        ("logical_inconsistencies", {"multistage_depth": 20, "num_attempts": 1}),
        ("past_tense", {"num_attempts": 1}),
        ("pair", {
            "custom_dataset": None,
            "language": "any",
            "multistage_depth": 20,
            "num_attempts": 1
        }),
        ("shuffle", {
            "custom_dataset": None,
            "language": "any",
            "num_attempts": 1,
            "num_transformations": 5
        }),
        ("sycophancy", {"multistage_depth": 20, "num_attempts": 1}),
        ("system_prompt_leakage", {"custom_dataset": None, "multistage_depth": 20, "num_attempts": 1}),
        ("ucar", {"language": "any", "num_attempts": 1}),
    ],
    # Additional presets can be added here if needed
}
