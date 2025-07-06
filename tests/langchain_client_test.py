def langchain_client_openai_backend_test():
    """
    Tests OpenAI client from local llamator lib.
    """
    from llamator.client.specific_chat_clients import ClientLangChain

    backend = "open_ai"
    api_key = "lm-studio"
    base_url = "http://localhost:1234/v1"

    attack_model = ClientLangChain(
        backend=backend,
        openai_api_base=base_url,
        openai_api_key=api_key,
        temperature=0.1,
        system_prompts=["You are a strong model."],
    )

    tested_model = ClientLangChain(
        backend=backend,
        openai_api_base=base_url,
        openai_api_key=api_key,
        temperature=0.1,
        model_description="Support bot",
    )

    basic_tests_params = [
        ("aim_jailbreak", {"num_attempts": 1}),
        ("dan", {"num_attempts": 1}),
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
        config=config,
        basic_tests=basic_tests_params,
    )


if __name__ == "__main__":
    langchain_client_openai_backend_test()
