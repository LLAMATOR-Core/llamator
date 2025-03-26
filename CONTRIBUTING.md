# Contributing to LLAMATOR

Thank you for your interest in contributing to LLAMATOR!

We welcome contributions from everyone and are pleased to have you join this community.

This document provides guidelines and instructions for contributing to this project.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.10
- Git

### Setting Up Your Development Environment

1. **Fork the Repository**: Start by forking the repository on GitHub.

2. **Clone your fork**:
    ```bash
    git clone https://github.com/RomiconEZ/llamator.git
    ```

### Set Up a Virtual Environment

```bash
. ./setup_dev_env.sh
source venv/bin/activate  # On Unix or macOS
```

### Install Dependencies

Install the project dependencies in editable mode (with the '-e' argument).
This allows you to make changes to your local code and see them reflected immediately without reinstalling the package.

```bash
pip install -r requirements-dev.txt
```

### Install pre-commit

To ensure code quality we use pre-commit hook with several checks.

```bash
pre-commit install
```

### Run Tests

1) Go to `tests/test_local_llamator.py`.

2) Create `.env` from `.env.example` and fill in the necessary fields.

3) Run the function to perform testing depending on your LLM client.

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

## Get Started with Your First Contribution: Adding a New Test

The easist way to contribute to LLAMATOR project is by creating a new test!
This can be easily acheived by:

#### 1. Create a test file:
* Navigate to the `attacks` directory.
* Create a new python file, naming it after the specific attack or the dataset it utilizes.

#### 2. Set up your file.

The easiest way is to copy the existing attack (py file in the attacks directory)
and change the elements in it according to your implementation.

For multi-stage attack implementation see "What Drives the Multi-stage?" notes in [docs](https://romiconez.github.io/llamator/attacks_description.html).

#### 3. Creating datasets with texts for attacks.

All files containing attack texts or prompts must be in the `.parquet` format.

These files are stored in the `attack_data` folder.

#### 3. Add your attack file name to the `attack_loader.py` file:

```python
from ..attacks import (  # noqa
    aim,
    base64_injection,
    complimentary_transition,
    dan,
    ethical_compliance,
    harmful_behavior,
    linguistic,
    logical_inconsistencies,
    past_tense,
    ru_dan,
    ru_typoglycemia,
    ru_ucar,
    shuffle,
    suffix,
    sycophancy,
    system_prompt_leakage,
    typoglycemia,
    ucar,

    #TODO: YOUR TEST HERE
)
```

#### 4. Add your attack name to the docstring of `start_testing()` in `main.py` and `initial_validation.py` file:

```python
AvailableTests = [
    "aim_jailbreak",
    "base64_injection",
    "bon",
    "complimentary_transition",
    "do_anything_now_jailbreak",
    "ethical_compliance",
    "harmful_behavior",
    "linguistic_evasion",
    "logical_inconsistencies",
    "past_tense",
    "RU_do_anything_now_jailbreak",
    "RU_typoglycemia_attack",
    "RU_ucar",
    "shuffle",
    "suffix",
    "sycophancy",
    "system_prompt_leakage",
    "typoglycemia_attack",
    "ucar",

    #TODO: YOUR TEST HERE (in alphabetical order!)
]
```

#### 5. Add your attack to the `attack_descriptions.json` and `attack_descriptions.md` files.

Please pay attention to the `attack_descriptions.md` structure. Description should be the same as docstring of the attack class. If your attack has an original paper or repository, it would be nice if you mentioned it in docstring and `attack_descriptions.md`.

#### 6. Open a PR! Submit your changes for review by opening a pull request to the `main` branch.

## Submitting a Pull Request.

1. Update your branch.

   Fetch any new changes from the base branch and rebase your branch.
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Submit a Pull Request.

    Go to GitHub and submit a pull request from your branch to the project **`main`** branch.

3. Request reviews.

    Request reviews from other contributors listed as maintainers. If you receive a feedback - make any necessary changes and push them.

4. Merge.

    Once your pull request is approved, it will be merged into the **`main`** branch.
