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

# List of basic tests with parameters
basic_tests_params = [
    ("aim_jailbreak", {"num_attempts": 2}),
    ("base64_injection", {"num_attempts": 2}),
    ("bon", {"num_attempts": 2}),
    ("complimentary_transition", {"num_attempts": 2}),
    ("crescendo", {"num_attempts": 2}),
    # Add other tests as needed
]

# Configuration for testing
config = {
    "enable_logging": True,
    "enable_reports": True,
    "artifacts_path": "./artifacts",
    "debug_level": 1,
    "report_language": "en",
}

# Start testing
llamator.start_testing(
    attack_model=attack_model,
    tested_model=tested_model,
    config=config,
    basic_tests=basic_tests_params,
)
```

---

## Helper Functions

### `print_preset_tests_params_example`
Prints example configuration for presets to the console.

**Usage:**
```python
from llamator import print_preset_tests_params_example

# Print configuration for 'standard' preset
print_preset_tests_params_example("standard")

# Print configuration for all available tests
print_preset_tests_params_example("all")
```

### `get_preset_tests_params_example`
Returns a string containing example configurations for presets.

**Usage:**
```python
from llamator import get_preset_tests_params_example

# Get example for 'standard' preset
standard_preset = get_preset_tests_params_example("standard")
print(standard_preset)

# Get example for all available tests
all_tests_preset = get_preset_tests_params_example("all")
print(all_tests_preset)
```

### `print_chat_models_info`
Displays information about available LangChain chat models, including parameters.

**Usage:**
```python
from llamator import print_chat_models_info

# Print basic model info
print_chat_models_info()

# Print detailed model info with parameters
print_chat_models_info(detailed=True)
```

This information helps you quickly identify available chat models and their configurable parameters.

