def openai_client_lm_studio_test():
    """
    Tests OpenAI client from local llamator lib.
    """
    from llamator.client.specific_chat_clients import ClientOpenAI

    api_key = "lm-studio"
    base_url = "http://localhost:1234/v1"
    model = "model-identifier"

    attack_model = ClientOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1,
        system_prompts=["You are a strong model."],
    )

    tested_model = ClientOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1,
        model_description="Support bot",
    )

    judge_model = ClientOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1,
        system_prompts=["You are a judge model."],
    )

    basic_tests = [
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
        ("dan", {"language": "any", "num_attempts": 3}),
        ("deceptive_delight", {"custom_dataset": None, "num_attempts": 3}),
        ("dialogue_injection_devmode", {"custom_dataset": None, "num_attempts": 3}),
        ("dialogue_injection_continuation", {"custom_dataset": None, "language": "any", "num_attempts": 3}),
        ("ethical_compliance", {"custom_dataset": None, "num_attempts": 3}),
        ("harmbench", {"custom_dataset": None, "language": "any", "num_attempts": 3}),
        ("linguistic_evasion", {"num_attempts": 3}),
        ("linguistic_sandwich", {"custom_dataset": None, "num_attempts": 3, "num_translations": 5}),
        ("logical_inconsistencies", {"multistage_depth": 20, "num_attempts": 3}),
        ("pair", {"custom_dataset": None, "language": "any", "multistage_depth": 20, "num_attempts": 3}),
        ("shuffle", {"custom_dataset": None, "language": "any", "num_attempts": 3, "num_transformations": 5}),
        ("suffix", {"custom_dataset": None, "num_attempts": 3}),
        ("sycophancy", {"multistage_depth": 20, "num_attempts": 3}),
        ("system_prompt_leakage", {"custom_dataset": None, "multistage_depth": 20, "num_attempts": 3}),
        ("time_machine", {"custom_dataset": None, "language": "any", "num_attempts": 3, "time_context": "any"}),
        ("ucar", {"language": "any", "num_attempts": 3}),
    ]

    config = {
        "enable_logging": True,  # Enable logging
        "enable_reports": True,  # Enable report generation
        "artifacts_path": "./artifacts",  # Path to the directory for saving artifacts
        "debug_level": 1,  # Logging level: 0 - WARNING, 1 - INFO, 2 - DEBUG
        "report_language": "en",  # Report language: 'en', 'ru'
    }

    from llamator.main import start_testing

    start_testing(
        attack_model=attack_model,
        tested_model=tested_model,
        judge_model=judge_model,
        config=config,
        basic_tests=basic_tests,
    )


if __name__ == "__main__":
    openai_client_lm_studio_test()
