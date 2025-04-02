import importlib
import os

from dotenv import load_dotenv


def test_openai_client():
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
    load_dotenv()

    import llamator.client.specific_chat_clients
    import llamator.main

    importlib.reload(llamator.client.specific_chat_clients)
    importlib.reload(llamator.main)

    from llamator.client.specific_chat_clients import ClientOpenAI

    api_key = os.getenv("OPENAI_CLIENT_API_KEY")
    base_url = os.getenv("OPENAI_CLIENT_BASEURL")
    model = os.getenv("OPENAI_CLIENT_MODEL")

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

    tests_with_attempts = [
        ("aim_jailbreak", 2),
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
        tests_with_attempts=tests_with_attempts,
        multistage_depth=2,
    )


def test_langchain_client():
    """
    Tests LangChain client from local llamator lib using OpenAI backend.

    Environment variables
    ----------
    OPENAI_CLIENT_API_KEY : str
        API key for OpenAI compatible API
    OPENAI_CLIENT_BASEURL : str
        URL of OpenAI compatible API
    OPENAI_CLIENT_MODEL : str
        Type of model
    """
    load_dotenv()

    import llamator.client.specific_chat_clients
    import llamator.main

    importlib.reload(llamator.client.specific_chat_clients)
    importlib.reload(llamator.main)

    api_key = os.getenv("OPENAI_CLIENT_API_KEY")
    base_url = os.getenv("OPENAI_CLIENT_BASEURL")
    model = os.getenv("OPENAI_CLIENT_MODEL")

    from llamator.client.specific_chat_clients import ClientLangChain

    attack_model = ClientLangChain(
        backend="open_ai",
        api_key=api_key,
        base_url=base_url,
        model=model,
        system_prompts=["You are a model for generating attacks on other models"],
    )

    tested_model = ClientLangChain(
        backend="open_ai",
        api_key=api_key,
        base_url=base_url,
        model=model,
        model_description="Support bot",
    )

    tests_with_attempts = [
        ("aim_jailbreak", 2),
        # ("base64_injection", 2),
        # ("bon", 2),
        # ("complimentary_transition", 2),
        # ("crescendo", 2),
        # ("do_anything_now_jailbreak", 2),
        # ("RU_do_anything_now_jailbreak", 2),
        # ("ethical_compliance", 2),
        # ("harmful_behavior", 2),
        # ("harmful_behavior_multistage", 2),
        # ("linguistic_evasion", 2),
        # ("logical_inconsistencies", 2),
        # ("past_tense", 2),
        # ("shuffle", 2),
        # ("suffix", 2),
        # ("sycophancy", 2),
        # ("system_prompt_leakage", 2),
        # ("typoglycemia_attack", 2),
        # ("RU_typoglycemia_attack", 2),
        # ("ucar", 2),
        # ("RU_ucar", 2),
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
        tests_with_attempts=tests_with_attempts,
        multistage_depth=2,
    )
