# Contributing to LLAMATOR

Thank you for your interest in contributing to LLAMATOR!

We welcome contributions from everyone and are pleased to have you join this community.

This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.9, 3.10, or 3.11
- Git

### Setting Up Your Development Environment

1. **Fork the Repository**: Start by forking the repository on GitHub.

2. **Clone your fork**:
    ```bash
    git clone https://github.com/LLAMATOR-Core/llamator.git
    ```

### Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Unix or macOS
```

### Install Dependencies

Install the project dependencies in editable mode (with the '-e' argument). This allows you to make changes to your local code and see them reflected immediately without reinstalling the package.

```bash
pip install -r requirements-dev.txt
```

### Install pre-commit

To ensure code quality we use pre-commit hook with several checks.

```bash
pre-commit install
```

### Run Tests

1. Navigate to `tests/test_local_llamator.py`.
2. Create `.env` from `.env.example` and fill in the necessary fields.
3. Run the test function based on your LLM client setup.

## Making Changes

1. Always create a new side-branch for your work from the **`main`** branch.

    ```bash
    git checkout main
    git checkout -b your-branch-name
    ```

2. Make your changes to the code and add or modify unit tests as necessary.

3. Run tests again.

4. Commit Your Changes.

    Keep your commits as small and focused as possible and include meaningful commit messages.
    ```bash
    git add .
    git commit -m "Add a brief description of your change"
    ```

5. Push the changes you did to GitHub.

    ```bash
    git push origin your-branch-name
    ```

## Adding a New Attack

Follow these steps to add a new attack to LLAMATOR:

### 1. Create Attack File

- Navigate to the `attacks` directory.
- Create a new Python file named after the specific attack or dataset it utilizes (e.g., `new_attack.py`).

### 2. Define Your Attack Class

Use this template to ensure proper integration:

```python
import logging
from typing import Generator, Optional

from ..attack_provider.attack_registry import register_test
from ..attack_provider.test_base import StatusUpdate, TestBase
from ..client.attack_config import AttackConfig
from ..client.chat_client import ChatSession
from ..client.client_config import ClientConfig

logger = logging.getLogger(__name__)

@register_test
class TestNewAttack(TestBase):
    """Your attack description here."""

    info = {
        "name": "New Attack",
        "code_name": "new_attack",
        "tags": [
            "lang:any",  # languages of available tested models
            "dialog:single-stage",  # type of dialogs: single-stage or multi-stage
            "owasp:llm01",  # OWASP TOP 10 for LLM risks
            "eval:heuristic",  # type of resilience evaluation: heuristic or llm-as-a-judge
            "arxiv:2504.11111",  # original paper if exists
            "model:llm",  # type of testing model: llm, vlm
        ],
        "description": {
            "en": "Your attack description here in English.",
            "ru": "Описание атаки на русском.",
        },
        "github_link": "Link to attack in release branch",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
        **kwargs,
    ):
        super().__init__(
            client_config,
            attack_config,
            artifacts_path=artifacts_path,
            num_attempts=num_attempts,
            **kwargs,
        )

    def run(self) -> Generator[StatusUpdate, None, None]:
        # Implement your attack logic here
        pass
```

### 3. Register Your Attack

In `attack_loader.py`, add:

```python
from ..attacks import (
    aim,
    base64_injection,
    #...
    new_attack,  # Your new attack
)
```

### 4. Add Your Attack to Documentation

Add info about your attack to `docs/attack_descriptions.md`, observing the structure and alphabetical order.

### 5. Test Your Attack

Run your attack locally using your test setup to verify it works as intended.

### 6. Open a Pull Request

Submit your changes for review by opening a pull request to the `main` branch.

## Submitting a Pull Request

1. Update your branch with the latest changes.

   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Open a Pull Request on GitHub.

3. Request a review from maintainers.

4. Incorporate feedback as needed.

5. Once approved, your changes will be merged.
