# How To Use

## Notebooks Examples

* 📄 [RAG bot testing via REST API](https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-api.ipynb)
* 🧙‍♂️ [Gandalf web bot testing via Selenium](https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-selenium.ipynb)
* 💬 [Telegram bot testing via Telethon](https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-telegram.ipynb)
* 📱 [WhatsApp bot testing via Selenium](https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-whatsapp.ipynb)
* 🔗 [LangChain client testing with custom attack](https://github.com/LLAMATOR-Core/llamator/blob/release/examples/llamator-langchain-custom-attack.ipynb)
* 🐋 [Running LLAMATOR in Docker](https://github.com/LLAMATOR-Core/llamator/blob/release/docker)

## Installation Guide

```bash
pip install llamator==2.3.1
```

## Usage Guide (using LM Studio)

```python
import llamator

# Initialize the attack model
attack_model = llamator.ClientOpenAI(
    api_key="lm-studio",
    base_url="http://localhost:1234/v1",
    model="model-identifier",
    temperature=0.1,
    system_prompts=["You are an attacking model."],
)

# Initialize the tested model
tested_model = llamator.ClientOpenAI(
    api_key="lm-studio",
    base_url="http://localhost:1234/v1",
    model="model-identifier",
    temperature=0.1,
    model_description="Model description",
)

# List of tests with the number of attempts
tests_with_attempts = [
    ("aim_jailbreak", 2),
    ("base64_injection", 2),
    ("bon", 2),
    ("complimentary_transition", 2),
    ("crescendo", 2),
    # Uncomment the following lines to include additional tests
    # ("do_anything_now_jailbreak", 2),
    # ("RU_do_anything_now_jailbreak", 2),
    # ("ethical_compliance", 2),
    # ("harmful_behavior", 2),
    # ("harmful_behavior_multistage", 2),
    # ("linguistic_evasion", 2),
    # ("logical_inconsistencies", 2),
    # ("past_tense", 2),
    # ("suffix", 2),
    # ("sycophancy", 2),
    # ("system_prompt_leakage", 2),
    # ("typoglycemia_attack", 2),
    # ("RU_typoglycemia_attack", 2),
    # ("ucar", 2),
    # ("RU_ucar", 2),
]

# Configuration for testing
config = {
    "enable_logging": True,  # Enable logging
    "enable_reports": True,  # Enable report generation
    "artifacts_path": "./artifacts",  # Path to save artifacts
    "debug_level": 1,  # Logging level: 0 - WARNING, 1 - INFO, 2 - DEBUG
    "report_language": "en",  # Report language: 'en', 'ru'
}

# Start testing
llamator.start_testing(
    attack_model=attack_model,
    tested_model=tested_model,
    config=config,
    tests_with_attempts=tests_with_attempts,
    multistage_depth=20,
)
```
