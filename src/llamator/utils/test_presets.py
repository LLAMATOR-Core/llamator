# File: llamator/src/llamator/utils/test_presets.py
"""
This module contains preset configurations for basic_tests_params.
Each preset is a list of tuples, where each tuple consists of a test code name and a dictionary of parameters.
Allowed preset names are "standard" and "all".
"""
preset_configs = {
    "standard": [
        ("suffix", {"num_attempts": 0}),
        ("aim_jailbreak", {"num_attempts": 0}),
        ("base64_injection", {"num_attempts": 0}),
        ("bon", {"num_attempts": 0, "multistage_depth": 5, "sigma": 0.4}),
        ("complimentary_transition", {"num_attempts": 0}),
        ("crescendo", {"num_attempts": 0, "multistage_depth": 20}),
        ("dan", {"num_attempts": 0}),
        ("RU_dan", {"num_attempts": 0}),
        ("ethical_compliance", {"num_attempts": 0}),
        ("harmful_behavior", {"num_attempts": 0}),
        ("harmful_behavior_multistage", {"num_attempts": 0, "multistage_depth": 20}),
        ("linguistic_evasion", {"num_attempts": 0}),
        ("logical_inconsistencies", {"num_attempts": 0, "multistage_depth": 20}),
        ("past_tense", {"num_attempts": 0}),
        ("shuffle", {"num_attempts": 0}),
        ("sycophancy", {"num_attempts": 0, "multistage_depth": 20}),
        ("system_prompt_leakage", {"num_attempts": 0, "multistage_depth": 20}),
        ("typoglycemia_attack", {"num_attempts": 0}),
        ("RU_typoglycemia_attack", {"num_attempts": 0}),
        ("ucar", {"num_attempts": 0}),
        ("RU_ucar", {"num_attempts": 0}),
    ],
    # Additional presets can be added here if needed
}
