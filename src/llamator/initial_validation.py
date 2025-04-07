# llamator/src/llamator/initial_validation.py

import logging
import os
from typing import List, Type, Tuple, Dict

from .attack_provider.attack_registry import test_classes
from .attack_provider.test_base import TestBase
from .client.chat_client import ClientBase
from .utils.params_example import _get_class_init_params


def get_registered_test_code_names() -> List[str]:
    """
    Returns a list of all registered test code names, based on the @register_test decorator
    and the 'code_name' field in each test class's info dictionary.
    """
    code_names = []
    for cls in test_classes:
        if hasattr(cls, "info") and "code_name" in cls.info:
            code_names.append(cls.info["code_name"])
    return code_names


def validate_model(client_model: ClientBase) -> bool:
    """
    Validates the model by sending a simple test request to ensure it can process input.

    Parameters
    ----------
    client_model : ClientBase
        The model to validate.

    Returns
    -------
    bool
        True if the model responded with content, otherwise False.
    """
    try:
        # Test message to check model functionality
        history = []
        message = [{"role": "user", "content": "Test message"}]
        response = client_model.interact(history, message)

        if "content" in response and response["content"]:
            logging.info(f"The model passed validation with response: {response['content']}")
            return True
        else:
            logging.error("The model's response does not contain 'content'.")
            return False
    except Exception as e:
        logging.error(f"Model validation failed: {e}")
        return False


def validate_tests(tests: List[str]) -> bool:
    """
    Checks whether each test in the provided list is registered.
    Previously a static list was used, now it is determined dynamically from registered test classes.

    Parameters
    ----------
    tests : List[str]
        The list of test code names to verify.

    Returns
    -------
    bool
        True if all tests are valid, otherwise False.
    """
    available_tests = get_registered_test_code_names()
    invalid_tests = [test for test in tests if test not in available_tests]
    if invalid_tests:
        logging.error(f"Invalid tests: {', '.join(invalid_tests)}")
        return False
    return True


def validate_custom_tests(custom_tests: List[Type[TestBase]]) -> bool:
    """
    Verifies that each custom test in the list is a subclass of TestBase.

    Parameters
    ----------
    custom_tests : List[Type[TestBase]]
        A list of custom test classes.

    Returns
    -------
    bool
        True if all custom tests are valid, otherwise False.
    """
    for test in custom_tests:
        if not issubclass(test, TestBase):
            logging.error(f"Test {test.__name__} is not a subclass of TestBase.")
            return False
    return True


def validate_artifacts_path(artifacts_path: str) -> bool:
    """
    Checks whether the artifacts path exists or tries to create it if it does not exist.

    Parameters
    ----------
    artifacts_path : str
        Path to the folder that will store artifacts (logs, reports, etc.).

    Returns
    -------
    bool
        True if the path is valid (exists or was successfully created), otherwise False.
    """
    try:
        if not os.path.exists(artifacts_path):
            logging.info(f"Artifacts path '{artifacts_path}' does not exist. Creating now...")
            os.makedirs(artifacts_path, exist_ok=True)
            logging.info(f"Artifacts path '{artifacts_path}' created successfully.")
        return True
    except Exception as e:
        logging.error(f"Failed to create or validate artifacts path: {e}")
        return False


def validate_language(language: str) -> str:
    """
    Validates the requested report language. Defaults to 'en' if an unsupported code is provided.

    Parameters
    ----------
    language : str
        The language code to validate (e.g. 'en' or 'ru').

    Returns
    -------
    str
        The validated language code. If the provided language is not supported, 'en' is returned.
    """
    try:
        supported_languages = {"en", "ru"}
        if language not in supported_languages:
            logging.warning(f"Unsupported language '{language}'. Defaulting to 'en'.")
            return "en"
        return language
    except Exception as e:
        logging.error(f"Failed to validate language: {e}. Defaulting to 'en'.")
        return "en"


def validate_basic_tests_params(basic_tests_params: List[Tuple[str, Dict]]) -> bool:
    """
    Checks that for each test in basic_tests_params, only parameters actually present in
    that test class's constructor are passed.

    Parameters
    ----------
    basic_tests_params : List[Tuple[str, Dict]]
        A list of tuples (code_name, {parameters}), where code_name is the test's
        registered code name, and {parameters} is a dictionary of parameters meant
        for that test's constructor.

    Returns
    -------
    bool
        True if all parameters match the corresponding test class's constructor, otherwise False.
    """
    # Build a mapping from test code_name to its class
    code_name_to_class = {}
    for cls in test_classes:
        if hasattr(cls, "info") and "code_name" in cls.info:
            code_name = cls.info["code_name"]
            code_name_to_class[code_name] = cls

    # Validate the parameters for each test
    for test_code_name, param_dict in basic_tests_params:
        if test_code_name not in code_name_to_class:
            # This is also checked in validate_tests, but handle it if it appears here
            logging.error(f"Test '{test_code_name}' is not registered.")
            return False

        cls = code_name_to_class[test_code_name]

        # Get the constructor parameters using the existing function
        init_params = _get_class_init_params(cls)
        recognized_param_names = set(init_params.keys())

        # Ensure all passed keys are recognized in the constructor
        for param_key in param_dict.keys():
            if param_key not in recognized_param_names:
                logging.error(
                    f"Test '{test_code_name}' has an unrecognized parameter '{param_key}' in basic_tests_params."
                )
                return False

    return True