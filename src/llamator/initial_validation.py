import logging
import os
from typing import List, Type

from .attack_provider.run_tests import TestBase
from .client.chat_client import ClientBase

AvailableTests = [
    "aim_jailbreak",
    "base64_injection",
    "complimentary_transition",
    "do_anything_now_jailbreak",
    "RU_do_anything_now_jailbreak",
    "ethical_compliance",
    "harmful_behavior",
    "linguistic_evasion",
    "self_refine",
    "RU_self_refine",
    "sycophancy_test",
    "typoglycemia_attack",
    "RU_typoglycemia_attack",
    "ucar",
    "RU_ucar",
    "amnesia",
    "authoritative_role_impersonation",
    "contextual_redirection",
    "affirmative_suffix",
    "system_prompt_stealer",
]


def validate_model(client_model: ClientBase) -> bool:
    """
    Validates the functionality of the model by invoking its interact method with test data.

    Parameters
    ----------
    client_model : ClientBase
        The model to be validated.

    Returns
    -------
    bool
        True if the model successfully processed the test request, otherwise False.
    """
    try:
        # Test message to validate the model's functionality
        history = []
        message = [{"role": "user", "content": "Test message"}]
        response = client_model.interact(history, message)

        if "content" in response and response["content"]:
            logging.info(f"The model passed the validation: {response['content']}")
            return True
        else:
            logging.error("The model's response does not contain content.")
            return False
    except Exception as e:
        logging.error(f"Model validation failed: {e}")
        return False


def validate_tests(tests: List[str]) -> bool:
    """
    Validates that each test from the provided list is present in the AvailableTests list.

    Parameters
    ----------
    tests : List[str]
        List of tests to be executed.

    Returns
    -------
    bool
        True if all tests are valid, otherwise False.
    """
    invalid_tests = [test for test in tests if test not in AvailableTests]
    if invalid_tests:
        logging.error(f"Invalid tests: {', '.join(invalid_tests)}")
        return False
    return True


def validate_custom_tests(custom_tests: List[Type[TestBase]]) -> bool:
    """
    Validates that each custom test is a subclass of TestBase.

    Parameters
    ----------
    custom_tests : List[Type[TestBase]]
        List of custom tests.

    Returns
    -------
    bool
        True if all custom tests are valid, otherwise False.
    """
    for test in custom_tests:
        if not issubclass(test, TestBase):  # Using issubclass to check class inheritance
            logging.error(f"Test {test.__name__} is not a subclass of TestBase.")
            return False
    return True


def validate_artifacts_path(artifacts_path: str) -> bool:
    """
    Validate that the artifacts path exists, or create it if it doesn't.

    Parameters
    ----------
    artifacts_path : str
        The path to the folder where artifacts (logs, reports) will be saved.

    Returns
    -------
    bool
        Returns True if the path is valid (exists or successfully created),
        otherwise returns False.
    """
    try:
        # Check if the path exists, if not, create the directory
        if not os.path.exists(artifacts_path):
            logging.info(f"Artifacts path '{artifacts_path}' does not exist. Creating...")
            os.makedirs(artifacts_path, exist_ok=True)
            logging.info(f"Artifacts path '{artifacts_path}' created successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to validate or create artifacts path: {e}")
        return False
