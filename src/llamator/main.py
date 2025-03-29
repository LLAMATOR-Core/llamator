import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Type

import colorama
from colorama import Style, Fore
from dotenv import load_dotenv

from .attack_provider.run_tests import setup_models_and_tests
from .attack_provider.test_base import TestBase
from .client.chat_client import ClientBase
from .format_output.logo import print_logo
from .format_output.draw_utils import (
    get_top_border,
    get_bottom_border,
    format_box_line,
    format_centered_line,
    get_separator_line
)
from .initial_validation import (
    validate_artifacts_path,
    validate_custom_tests,
    validate_language,
    validate_model,
    validate_tests,
)
from .logging import setup_logging
from .report_generators.excel_report_generator import create_attack_report_from_artifacts
from .report_generators.word_report_generator import create_word_report

# At this stage, the api keys that the user sets are loaded
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)
colorama.init()

# Defining constants for text reset and brightness
RESET = Style.RESET_ALL
BRIGHT = Style.BRIGHT
BRIGHT_CYAN = Fore.CYAN + Style.BRIGHT
BRIGHT_RED = Fore.RED + Style.BRIGHT
BRIGHT_GREEN = Fore.GREEN + Style.BRIGHT

def start_testing(
    attack_model: ClientBase,
    judge_model: Optional[ClientBase],
    tested_model: ClientBase,
    config: dict,
    num_threads: Optional[int] = 1,
    basic_tests_params: Optional[List[Tuple[str, Dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], Dict]]] = None,
):
    """
    Start testing.

    Parameters
    ----------
    attack_model : ClientBase
        The attacking model used to generate tests.
    judge_model : ClientBase, optional
        The judge model used to evaluate test responses.
    tested_model : ClientBase
        The model being tested against the attacks.
    config : dict
        Configuration dictionary with the following keys:

        - 'enable_logging' : bool
            Whether to enable logging.
        - 'enable_reports' : bool
            Whether to generate xlsx reports.
        - 'artifacts_path' : Optional[str]
            Path to the folder for saving artifacts.
        - 'debug_level' : int
            Level of logging verbosity (default is 1).
            debug_level = 0 - WARNING.
            debug_level = 1 - INFO.
            debug_level = 2 - DEBUG.
        - 'report_language' : str
            Language for the report (default is 'en').
            Possible values: 'en', 'ru'.

    num_threads : int, optional
        Number of threads for parallel test execution (default is 1).
    basic_tests_params : List[Tuple[str, dict]], optional
        List of test names and parameter dictionaries for standard tests (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    custom_tests_params : List[Tuple[Type[TestBase], Dict]], optional
        List of custom test classes and parameter dictionaries (default is None).
        The dictionary keys and значения будут переданы в конструктор тестового класса.

    Returns
    -------
    None
    """

    # Extract values from the config dictionary
    enable_logging = config.get("enable_logging", True)
    enable_reports = config.get("enable_reports", False)
    artifacts_path = config.get("artifacts_path", None)
    debug_level = config.get("debug_level", 1)
    report_language = config.get("report_language", "en")

    start_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if artifacts_path is None:
        enable_logging = False
        enable_reports = False
        artifacts_run_path = None
        print(f"{BRIGHT_CYAN}ℹ{RESET} Logging and reports have been disabled.")
    else:
        # Validate the artifacts path
        if not validate_artifacts_path(artifacts_path):
            print(f"{BRIGHT_RED}✘{RESET} Invalid artifacts path.")
            return
        elif enable_reports is True or enable_logging is True:
            # Create a new folder named 'LLAMATOR_run_{start_timestamp}' inside artifacts_path
            run_folder_name = f"LLAMATOR_run_{start_timestamp}"
            run_folder_path = os.path.join(artifacts_path, run_folder_name)
            os.makedirs(run_folder_path, exist_ok=True)

            # Update artifacts_path to point to the new run folder
            artifacts_run_path = run_folder_path
            print(f"{BRIGHT_CYAN}ℹ{RESET} Artifacts will be saved to: {artifacts_run_path}")

    # Setup logging if enabled
    if enable_logging:
        setup_logging(debug_level, artifacts_run_path)
        print(f"{BRIGHT_CYAN}ℹ{RESET} Logging has been set up with debug level: {debug_level}")

    # Program logo output
    print_logo()

    # Print configuration summary using functions from draw_utils
    box_width = 60  # Fixed total width for the box
    print(get_top_border(box_width))
    print(format_centered_line("Testing Configuration", box_width))
    print(get_separator_line(box_width))
    threads_text = f"Number of threads: {num_threads}"
    logging_text = f"Logging enabled: {enable_logging}"
    reports_text = f"Reports enabled: {enable_reports}"
    language_text = f"Report language: {report_language}"
    print(format_box_line(threads_text, box_width))
    print(format_box_line(logging_text, box_width))
    print(format_box_line(reports_text, box_width))
    print(format_box_line(language_text, box_width))
    print(get_bottom_border(box_width))
    print()

    # Validate attack model
    print(f"{BRIGHT_CYAN}Validating models...{RESET}")
    if not validate_model(attack_model):
        print(f"{BRIGHT_RED}✘{RESET} Attack model failed validation.")
        return
    else:
        print(f"{BRIGHT_GREEN}✓{RESET} Attack model validated successfully.")

    # Validate judge model only if it is not None
    if judge_model is not None:
        if not validate_model(judge_model):
            print(f"{BRIGHT_RED}✘{RESET} Judge model failed validation.")
            return
        else:
            print(f"{BRIGHT_GREEN}✓{RESET} Judge model validated successfully.")
    else:
        print(f"{BRIGHT_CYAN}ℹ{RESET} No judge model specified.")

    # Validate tested model
    if not validate_model(tested_model):
        print(f"{BRIGHT_RED}✘{RESET} Tested model failed validation.")
        return
    else:
        print(f"{BRIGHT_GREEN}✓{RESET} Tested model validated successfully.")

    # Validate the test list
    if basic_tests_params and not validate_tests([test[0] for test in basic_tests_params]):
        print(f"{BRIGHT_RED}✘{RESET} The test list contains invalid values.")
        return
    else:
        print(f"{BRIGHT_GREEN}✓{RESET} Test list validated successfully.")

    # Validate custom tests
    if custom_tests_params and not validate_custom_tests([test[0] for test in custom_tests_params]):
        print(f"{BRIGHT_RED}✘{RESET} One or more custom tests failed validation.")
        return
    elif custom_tests_params:
        print(f"{BRIGHT_GREEN}✓{RESET} Custom tests validated successfully.")

    setup_models_and_tests(
        attack_model=attack_model,
        judge_model=judge_model,
        tested_model=tested_model,
        num_threads=num_threads,
        basic_tests_params=basic_tests_params,
        custom_tests_params=custom_tests_params,
        artifacts_path=artifacts_run_path if enable_reports else None,
    )

    logging.info("Completion of testing")

    # Explicitly close log files at the end of the program
    for handler in logging.getLogger().handlers:
        from logging.handlers import RotatingFileHandler
        if isinstance(handler, RotatingFileHandler):
            handler.close()

    if enable_reports:
        report_language = validate_language(report_language)
        csv_folder_name = "csv_report"
        print(
            f"{BRIGHT_RED}DISCLAIMER: Report may contain HARMFUL and OFFENSIVE language, reader discretion is recommended.{RESET}"
        )

        print(f"{BRIGHT_CYAN}Generating reports...{RESET}")
        create_attack_report_from_artifacts(
            artifacts_dir=artifacts_run_path, csv_folder_name=csv_folder_name, report_file_name="attacks_report.xlsx"
        )
        create_word_report(
            artifacts_dir=artifacts_run_path,
            csv_folder_name=csv_folder_name,
            docx_file_name="attacks_report.docx",
            language=report_language,
        )

    # Final message with a properly aligned decorative border
    box_width = 60  # Fixed total width for consistency
    print(get_top_border(box_width))
    thank_you_text = "Thank you for using LLAMATOR!"
    print(format_centered_line(thank_you_text, box_width))
    print(get_bottom_border(box_width))
    logging.shutdown()