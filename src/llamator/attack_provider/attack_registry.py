# llamator/src/llamator/attack_provider/attack_registry.py
import logging
import os
from typing import Dict, List, Optional, Tuple, Type

from ..attack_provider.test_base import TestBase
from ..client.attack_config import AttackConfig
from ..client.client_config import ClientConfig
from ..client.judge_config import JudgeConfig

logger = logging.getLogger(__name__)

# Registry of attack test classes
test_classes = []


# Decorator used to register attack test classes
def register_test(cls) -> None:
    """
    Decorator that registers test types.

    Parameters
    ----------
    cls : class
        The class of the test that needs to be registered.
    """
    global test_classes
    logger.debug(f"Registering attack test class: {cls.__name__}")
    test_classes.append(cls)
    return


def instantiate_tests(
    client_config: ClientConfig,
    attack_config: AttackConfig,
    judge_config: Optional[JudgeConfig] = None,
    basic_tests_params: Optional[List[Tuple[str, Dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], Dict]]] = None,
    artifacts_path: Optional[str] = None,
) -> List[TestBase]:
    """
    Instantiate and return a list of test instances based on registered test classes
    and custom test classes.

    Parameters
    ----------
    client_config : ClientConfig
        Configuration object for the client.
    attack_config : AttackConfig
        Configuration object for the attack.
    judge_config : JudgeConfig, optional
        Configuration object for the judge.
    basic_tests_params : List[Tuple[str, dict]], optional
        A list of basic test names and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    custom_tests_params : List[Tuple[Type[TestBase], dict]], optional
        A list of custom test classes and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    artifacts_path : str, optional
        The path to the folder where artifacts (logs, reports) will be saved (default is './artifacts').

    Returns
    -------
    List[TestBase]
        A list of instantiated test objects.
    """
    global test_classes

    csv_report_path = None

    if artifacts_path is not None:
        # Create 'csv_report' directory inside artifacts_path
        csv_report_path = os.path.join(artifacts_path, "csv_report")
        os.makedirs(csv_report_path, exist_ok=True)

    # List to store instantiated tests
    tests = []

    # Create instances of basic test classes
    if basic_tests_params is not None:
        basic_tests_dict = dict(basic_tests_params)
        for cls in test_classes:
            if cls.info["code_name"] in basic_tests_dict:
                test_kwargs = basic_tests_dict[cls.info["code_name"]]

                test_instance = cls(
                    client_config=client_config,
                    attack_config=attack_config,
                    judge_config=judge_config,
                    artifacts_path=csv_report_path,
                    **test_kwargs,
                )
                logger.debug(f"Instantiating attack test class: {cls.__name__} with kwargs: {test_kwargs}")
                tests.append(test_instance)

    # Process custom tests with parameters
    if custom_tests_params is not None:
        for custom_test_cls, test_kwargs in custom_tests_params:
            try:
                # Register custom test if not already registered so its info is available for reports
                if custom_test_cls not in test_classes:
                    logger.debug(f"Registering custom test class: {custom_test_cls.__name__}")
                    test_classes.append(custom_test_cls)
                test_instance = custom_test_cls(
                    client_config=client_config,
                    attack_config=attack_config,
                    judge_config=judge_config,
                    artifacts_path=csv_report_path,
                    **test_kwargs,
                )
                logger.debug(f"Instantiating custom test class: {custom_test_cls.__name__} with kwargs: {test_kwargs}")
                tests.append(test_instance)
            except Exception as e:
                logger.error(f"Error instantiating custom test {custom_test_cls.__name__}: {e}")

    # Return the list of all instantiated tests
    return tests
