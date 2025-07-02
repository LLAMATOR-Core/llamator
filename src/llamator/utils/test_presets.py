"""
This module contains preset configurations for basic_tests_params.
Each preset is a list of tuples, where each tuple consists of a test code name and a dictionary of parameters.
Allowed preset names are "standard", "vlm", and "all".
"""
preset_configs = {
    "standard": [
        ("suffix", {"custom_dataset": None, "num_attempts": 3}),
        ("aim_jailbreak", {"num_attempts": 3}),
        (
            "autodan_turbo",
            {
                "custom_dataset": None,
                "language": "any",
                "multistage_depth": 10,
                "num_attempts": 3,
                "strategy_library_size": 10,
            },
        ),
        ("base64_injection", {"custom_dataset": None, "num_attempts": 3}),
        ("bon", {"custom_dataset": None, "language": "any", "num_attempts": 3, "num_transformations": 5, "sigma": 0.4}),
        ("crescendo", {"custom_dataset": None, "language": "any", "multistage_depth": 5, "num_attempts": 3}),
        ("deceptive_delight", {"custom_dataset": None, "num_attempts": 3}),
        ("dialogue_injection_continuation", {"custom_dataset": None, "language": "any", "num_attempts": 3}),
        ("dialogue_injection_devmode", {"custom_dataset": None, "num_attempts": 3}),
        ("dan", {"language": "any", "num_attempts": 3}),
        ("ethical_compliance", {"custom_dataset": None, "num_attempts": 3}),
        ("harmbench", {"custom_dataset": None, "language": "any", "num_attempts": 3}),
        ("linguistic_evasion", {"num_attempts": 3}),
        ("logical_inconsistencies", {"multistage_depth": 20, "num_attempts": 3}),
        ("pair", {"custom_dataset": None, "language": "any", "multistage_depth": 20, "num_attempts": 3}),
        ("shuffle", {"custom_dataset": None, "language": "any", "num_attempts": 3, "num_transformations": 5}),
        ("sycophancy", {"multistage_depth": 20, "num_attempts": 3}),
        ("system_prompt_leakage", {"custom_dataset": None, "multistage_depth": 20, "num_attempts": 3}),
        ("time_machine", {"custom_dataset": None, "language": "any", "num_attempts": 3, "time_context": "both"}),
        ("ucar", {"language": "any", "num_attempts": 3}),
    ],
    "vlm": [
        (
            "vlm_lowres_docs",
            {
                "custom_pdf_dir": None,
                "is_long_pdf": False,
                "num_attempts": 3,
                "overwrite_existing_pdfs": False,
                "rescale": 0.25,
            },
        ),
        (
            "vlm_m_attack",
            {
                "attack_data_base": None,
                "attack_source": "parquet",
                "dataset": "bigscale_100",
                "dataset_variations": None,
                "num_attempts": 3,
            },
        ),
        ("vlm_text_hallucination", {"attack_types": None, "num_attempts": 3}),
    ],
    # Additional presets can be added here if needed
}
