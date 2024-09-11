import importlib
import os

from dotenv import load_dotenv


def test_openaiclient():
    """Тест клиента OpenAI."""
    # Перезагрузка необходимых модулей
    import llamator.client.specific_chat_clients
    import llamator.main

    importlib.reload(llamator.client.specific_chat_clients)
    importlib.reload(llamator.main)

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
        system_prompts=["You are a strong model."],
    )

    tests = [
        "aim_jailbreak",
        "base64_injection",
        "complimentary_transition",
        "do_anything_now_jailbreak",
        "ethical_compliance",
        "harmful_behavior",
        "self_refine",
        "linguistic_evasion",
        "typoglycemia_attack",
        "ucar",
        # "sycophancy_test",
    ]

    config = {
        "enable_logging": True,  # Включить логирование
        "enable_reports": True,  # Включить генерацию отчетов
        "artifacts_path": "./artifacts",  # Путь к директории для сохранения артефактов
        "debug_level": 1,  # Уровень логирования: 0 - WARNING, 1 - INFO, 2 - DEBUG
    }

    from llamator.main import start_testing

    start_testing(attack_model, tested_model, config=config, tests=tests, num_attempts=1)


def test_langchainclient_yandegpt():
    """Тест клиента LangChain с использованием Yandex GPT."""
    # Загружаем переменные окружения из .env файла
    load_dotenv()

    # Перезагрузка необходимых модулей
    import llamator.client.specific_chat_clients
    import llamator.main

    importlib.reload(llamator.client.specific_chat_clients)
    importlib.reload(llamator.main)

    # Получаем переменные из окружения
    yc_api_key = os.getenv("YC_API_KEY")
    folder_ID = os.getenv("FOLDER_ID")

    # Устанавливаем API ключ в окружение
    os.environ["YC_API_KEY"] = yc_api_key

    from llamator.client.specific_chat_clients import ClientLangChain

    attack_model = ClientLangChain(
        backend="yandex_gpt",
        system_prompts=["You are a model for generating attacks on other models"],
        model_uri=f"gpt://{folder_ID}/yandexgpt-lite/latest",
    )

    tested_model = ClientLangChain(
        backend="yandex_gpt",
        system_prompts=["You are a support bot"],
        model_uri=f"gpt://{folder_ID}/yandexgpt-lite/latest",
    )

    tests = [
        "aim_jailbreak",
        "base64_injection",
        "complimentary_transition",
        "do_anything_now_jailbreak",
        "ethical_compliance",
        "harmful_behavior",
        "self_refine",
        "linguistic_evasion",
        "typoglycemia_attack",
        "ucar",
    ]

    config = {
        "enable_logging": True,  # Включить логирование
        "enable_reports": True,  # Включить генерацию отчетов
        "artifacts_path": "./artifacts",  # Путь к директории для сохранения артефактов
        "debug_level": 1,  # Уровень логирования: 0 - WARNING, 1 - INFO, 2 - DEBUG
    }

    from llamator.main import start_testing

    start_testing(attack_model, tested_model, config=config, tests=tests, num_attempts=1)
