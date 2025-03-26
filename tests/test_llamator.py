import importlib
import os

from dotenv import load_dotenv


def test_openai_client():
    """
    Tests OpenAI client from public llamator lib.

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

    import llamator

    importlib.reload(llamator)

    api_key = os.getenv("OPENAI_CLIENT_API_KEY")
    base_url = os.getenv("OPENAI_CLIENT_BASEURL")
    model = os.getenv("OPENAI_CLIENT_MODEL")

    attack_model = llamator.ClientOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1,
        system_prompts=["You are a strong model."],
    )

    tested_model = llamator.ClientOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=0.1,
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

    llamator.start_testing(
        attack_model=attack_model,
        tested_model=tested_model,
        config=config,
        tests_with_attempts=tests_with_attempts,
        multistage_depth=2,
    )
