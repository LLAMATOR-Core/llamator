# llamator/src/llamator/main.py

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Dict, List, Optional, Tuple, Type

from dotenv import load_dotenv

from llamator.format_output.output_helpers import print_testing_configuration

from .attack_provider.run_tests import setup_models_and_tests
from .attack_provider.test_base import TestBase
from .client.chat_client import ClientBase
from .format_output.box_drawing import format_centered_line, get_bottom_border, get_top_border
from .format_output.color_consts import BRIGHT, BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_RED, RESET
from .format_output.logo import print_logo
from .initial_validation import (
    check_judge_config_usage,
    validate_artifacts_path,
    validate_basic_tests_params,
    validate_custom_tests,
    validate_language,
    validate_model,
    validate_tests,
)
from .logging import setup_logging
from .report_generators.excel_report_generator import create_attack_report_from_artifacts
from .report_generators.word_report_generator import create_word_report

# Load user-defined environment variables
dotenv_path = os.path.join(os.getcwd(), ".env")
load_dotenv(dotenv_path)


def validate_models_and_tests(
    attack_model: ClientBase,
    judge_model: Optional[ClientBase],
    tested_model: ClientBase,
    basic_tests_params: Optional[List[Tuple[str, Dict]]],
    custom_tests_params: Optional[List[Tuple[Type[TestBase], Dict]]],
) -> bool:
    """
    Validates the provided models and test configurations.

    Parameters
    ----------
    attack_model : ClientBase
        The model that will be used to generate attacks.
    judge_model : Optional[ClientBase]
        The model that will judge the responses.
    tested_model : ClientBase
        The model being tested.
    basic_tests_params : Optional[List[Tuple[str, Dict]]]
        A list of basic tests with parameter dictionaries.
    custom_tests_params : Optional[List[Tuple[Type[TestBase], Dict]]]
        A list of custom test classes with parameter dictionaries.

    Returns
    -------
    bool
        True if all validations succeed, otherwise False.
    """
    print(f"{BRIGHT_CYAN}Validating models and tests...{RESET}")

    if basic_tests_params and not validate_tests([test[0] for test in basic_tests_params]):
        print(f"{BRIGHT_RED}✘{RESET} The test list contains invalid code names.")
        return False
    else:
        if basic_tests_params:
            print(f"{BRIGHT_GREEN}✓{RESET} Test code names validated successfully.")

    if basic_tests_params and not validate_basic_tests_params(basic_tests_params):
        print(f"{BRIGHT_RED}✘{RESET} One or more test parameters are invalid.")
        return False
    else:
        if basic_tests_params:
            print(f"{BRIGHT_GREEN}✓{RESET} Basic test parameters validated successfully.")

    if custom_tests_params and not validate_custom_tests([test[0] for test in custom_tests_params]):
        print(f"{BRIGHT_RED}✘{RESET} One or more custom tests failed validation.")
        return False
    elif custom_tests_params:
        print(f"{BRIGHT_GREEN}✓{RESET} Custom tests validated successfully.")

    if not check_judge_config_usage(
        basic_tests_params if basic_tests_params else [],
        custom_tests_params if custom_tests_params else [],
        judge_model,
    ):
        print(f"{BRIGHT_RED}✘{RESET} Judge model is required for tests that specify 'judge_config'.")
        return False

    if not validate_model(attack_model):
        print(f"{BRIGHT_RED}✘{RESET} Attack model failed validation.")
        return False
    else:
        print(f"{BRIGHT_GREEN}✓{RESET} Attack model validated successfully.")

    if judge_model is not None:
        if not validate_model(judge_model):
            print(f"{BRIGHT_RED}✘{RESET} Judge model failed validation.")
            return False
        else:
            print(f"{BRIGHT_GREEN}✓{RESET} Judge model validated successfully.")
    else:
        print(f"{BRIGHT_CYAN}ℹ{RESET} No judge model specified.")

    if not validate_model(tested_model):
        print(f"{BRIGHT_RED}✘{RESET} Tested model failed validation.")
        return False
    else:
        print(f"{BRIGHT_GREEN}✓{RESET} Tested model validated successfully.")

    print()
    return True


def _rename_reports_with_timestamp(artifacts_run_path: str, start_timestamp: str) -> None:
    """
    Renames the 'csv_report' folder and its CSV files, as well as the Word/Excel reports
    and the main log file, appending a unique timestamp.

    Parameters
    ----------
    artifacts_run_path : str
        The path to the artifacts directory (for example: logs, CSV reports).
    start_timestamp : str
        The timestamp string (e.g. '2025-04-05_16-02-18') to be appended to file names.
    """
    csv_folder_name = "csv_report"

    try:
        # 1) Rename the csv_report folder
        old_csv_folder_path = os.path.join(artifacts_run_path, csv_folder_name)
        csv_folder_timestamped = f"{csv_folder_name}_{start_timestamp}"
        new_csv_folder_path = os.path.join(artifacts_run_path, csv_folder_timestamped)

        if os.path.isdir(old_csv_folder_path):
            os.rename(old_csv_folder_path, new_csv_folder_path)

            # 2) Append the timestamp to each CSV file inside the renamed folder
            for filename in os.listdir(new_csv_folder_path):
                if filename.lower().endswith(".csv"):
                    old_csv_file = os.path.join(new_csv_folder_path, filename)
                    base_name, ext = os.path.splitext(filename)
                    new_csv_name = f"{base_name}_{start_timestamp}{ext}"
                    new_csv_file = os.path.join(new_csv_folder_path, new_csv_name)
                    os.rename(old_csv_file, new_csv_file)

        # 3) Rename Excel and Word report files
        old_xlsx_path = os.path.join(artifacts_run_path, "attacks_report.xlsx")
        new_xlsx_path = os.path.join(artifacts_run_path, f"attacks_report_{start_timestamp}.xlsx")
        if os.path.isfile(old_xlsx_path):
            os.rename(old_xlsx_path, new_xlsx_path)

        old_docx_path = os.path.join(artifacts_run_path, "attacks_report.docx")
        new_docx_path = os.path.join(artifacts_run_path, f"attacks_report_{start_timestamp}.docx")
        if os.path.isfile(old_docx_path):
            os.rename(old_docx_path, new_docx_path)

        # 4) Rename log file
        old_log_path = os.path.join(artifacts_run_path, "LLAMATOR_runtime.log")
        new_log_path = os.path.join(artifacts_run_path, f"LLAMATOR_runtime_{start_timestamp}.log")
        if os.path.isfile(old_log_path):
            os.rename(old_log_path, new_log_path)

    except Exception as e:
        print(f"Unable to rename reports or files: {e}")


def start_testing(
    attack_model: ClientBase,
    tested_model: ClientBase,
    config: dict,
    judge_model: Optional[ClientBase] = None,
    num_threads: Optional[int] = 1,
    basic_tests: Optional[List[Tuple[str, Dict]]] = None,
    custom_tests: Optional[List[Tuple[Type[TestBase], Dict]]] = None,
) -> Dict[str, Dict[str, int]]:
    """
    The main entry point for launching tests.

    Parameters
    ----------
    attack_model : ClientBase
        The model that generates attacks.
    tested_model : ClientBase
        The model to be tested for vulnerabilities.
    config : dict
        Configuration dictionary with keys:

        - 'enable_logging': bool
            Whether to enable logging.
        - 'enable_reports': bool
            Whether to generate Excel/Word reports.
        - 'artifacts_path': Optional[str]
            Path to the folder for saving artifacts (logs, CSV, etc.).
        - 'debug_level': int
            Logging level (0=WARNING, 1=INFO, 2=DEBUG).
        - 'report_language': str
            Language code for the final report ('en' or 'ru').
    judge_model : Optional[ClientBase]
        The model that judges the responses (optional).
    num_threads : Optional[int]
        Number of threads to use for parallel testing.
    basic_tests : Optional[List[Tuple[str, Dict]]]
        A list of test code names and a dict of parameters for each test.
    custom_tests : Optional[List[Tuple[Type[TestBase], Dict]]]
        A list of custom test classes and parameter dictionaries.

    Returns
    -------
    Dict[str, Dict[str, int]]
        Aggregated results per attack. Empty dict if testing was not executed.
    """
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
        if not validate_artifacts_path(artifacts_path):
            print(f"{BRIGHT_RED}✘{RESET} Invalid artifacts path.")
            return {}
        elif enable_reports or enable_logging:
            run_folder_name = f"LLAMATOR_run_{start_timestamp}"
            run_folder_path = os.path.join(artifacts_path, run_folder_name)
            os.makedirs(run_folder_path, exist_ok=True)
            artifacts_run_path = str(run_folder_path)
            print(f"{BRIGHT_CYAN}ℹ{RESET} Artifacts will be saved to: {artifacts_run_path}")
        else:
            artifacts_run_path = None

    if enable_logging and artifacts_run_path is not None:
        setup_logging(debug_level, artifacts_run_path)
        print(f"{BRIGHT_CYAN}ℹ{RESET} Logging has been set up with debug level: {debug_level}")

    # Print the LLAMATOR logo
    print_logo(box_width=80)

    # Print test configuration
    print_testing_configuration(num_threads, enable_logging, enable_reports, report_language, 80)

    # Validate models, test codes, and parameters
    if not validate_models_and_tests(attack_model, judge_model, tested_model, basic_tests, custom_tests):
        return {}

    # Run tests
    results_dict = setup_models_and_tests(
        attack_model=attack_model,
        judge_model=judge_model,
        tested_model=tested_model,
        num_threads=num_threads,
        basic_tests_params=basic_tests,
        custom_tests_params=custom_tests,
        artifacts_path=artifacts_run_path if enable_reports else None,
    )

    logging.info("Completion of testing.")

    # Close log file handlers
    for handler in logging.getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.close()

    # Generate reports if enabled
    if enable_reports and artifacts_run_path:
        report_language = validate_language(report_language)
        print(
            f"{BRIGHT_RED}DISCLAIMER: Report may contain HARMFUL and OFFENSIVE language. Reader discretion is advised.{RESET}"
        )

        report_base_name = "attacks_report"

        print(f"{BRIGHT_CYAN}Generating reports...{RESET}")
        create_attack_report_from_artifacts(
            artifacts_dir=artifacts_run_path, csv_folder_name="csv_report", report_file_name=f"{report_base_name}.xlsx"
        )
        create_word_report(
            artifacts_dir=artifacts_run_path,
            csv_folder_name="csv_report",
            docx_file_name=f"{report_base_name}.docx",
            language=report_language,
        )

        _rename_reports_with_timestamp(artifacts_run_path, start_timestamp)

        print(f"Reports created: {artifacts_run_path}")
        excel_report_path = os.path.join(artifacts_run_path, f"{report_base_name}_{start_timestamp}.xlsx")
        word_report_path = os.path.join(artifacts_run_path, f"{report_base_name}_{start_timestamp}.docx")
        print(f"Excel report path: {excel_report_path}")
        print(f"Word report path: {word_report_path}")

    # Decorative border at the end
    box_width = 80
    print(get_top_border(box_width))
    thank_you_text = "Thank you for using LLAMATOR!"
    print(format_centered_line(thank_you_text, box_width))
    print(get_bottom_border(box_width))
    logging.shutdown()

    return results_dict
