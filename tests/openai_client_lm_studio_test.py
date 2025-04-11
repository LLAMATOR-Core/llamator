def openai_client_lm_studio_test():
    """
    Tests OpenAI client from local llamator lib.

    Environment variables
    ----------
    OPENAI_CLIENT_API_KEY : str
        API key for OpenAI compatible API
    OPENAI_CLIENT_BASEURL : str
        URL of OpenAI compatible API
    OPENAI_CLIENT_MODEL : str
        Type of model
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

    basic_tests_params = [
        ("RU_ucar", {"num_attempts": 1}),
        ("RU_dan", {"num_attempts": 1}),
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
        basic_tests=basic_tests_params,
    )


openai_client_lm_studio_test()
