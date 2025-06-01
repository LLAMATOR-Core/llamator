import textwrap
from typing import Dict, List, Tuple, Type

import colorama
from pydantic import ValidationError

from ..attack_provider.attack_loader import *
from ..attack_provider.attack_registry import instantiate_tests
from ..attack_provider.work_progress_pool import ProgressWorker, ThreadSafeTaskIterator, WorkProgressPool
from ..client.attack_config import AttackConfig
from ..client.chat_client import *
from ..client.client_config import ClientConfig
from ..client.judge_config import JudgeConfig
from ..format_output.color_consts import BRIGHT_RED, BRIGHT_YELLOW, GREEN, LIGHTBLUE, RED, RESET
from ..format_output.table_printing import print_table
from .test_base import StatusUpdate, TestBase, TestStatus

logger = logging.getLogger(__name__)

# Define desired column widths for Attack Type and Strength
ATTACK_TYPE_WIDTH = 25
STRENGTH_WIDTH = 20


def _aggregate_results(tests: List[TestBase]) -> Dict[str, Dict[str, int]]:
    """
    Build a compact dictionary with counters for every executed attack.

    Parameters
    ----------
    tests : List[TestBase]
        Executed test instances.

    Returns
    -------
    Dict[str, Dict[str, int]]
        {
            "aim_jailbreak": {"broken": 3, "resilient": 7, "errors": 0},
            ...
        }
    """
    result: Dict[str, Dict[str, int]] = {}
    for test in tests:
        result[test.info["code_name"]] = {
            "broken": test.status.breach_count,
            "resilient": test.status.resilient_count,
            "errors": test.status.error_count,
        }
    return result


class TestTask:
    """
    A class that wraps a test and provides a callable interface for running the test
    and updating progress during its execution.

    Parameters
    ----------
    test : TestBase
        An instance of a test that will be run when the object is called.

    Methods
    -------
    __call__(progress_worker: ProgressWorker)
        Executes the test and updates the progress worker with the test's status.
    """

    def __init__(self, test):
        # Store the test instance for later execution
        self.test = test

    def __call__(self, progress_worker: ProgressWorker):
        # Execute the test and store the result
        result = self.test.run()

        # Check if the result is an iterator (e.g., for status updates)
        if result and iter(result) is result:
            # Process iterable results
            for statusUpdate in self.test.run():
                statusUpdate: StatusUpdate
                color = RESET
                if statusUpdate.action == "Preparing":
                    color = LIGHTBLUE
                elif statusUpdate.action == "Attacking":
                    color = RED

                # Update the progress worker with the test's status
                progress_worker.update(
                    task_name=f"{color}{statusUpdate.action}: {statusUpdate.test_name}{RESET}",
                    progress=statusUpdate.progress_position,
                    total=statusUpdate.progress_total,
                    breach_count=statusUpdate.status.breach_count,
                    resilient_count=statusUpdate.status.resilient_count,
                    error_count=statusUpdate.status.error_count,
                    colour="BLUE",
                )

        # If the result is a status update
        elif result and isinstance(result, StatusUpdate):
            statusUpdate: StatusUpdate
            color = RESET
            if statusUpdate.action == "Preparing":
                color = LIGHTBLUE
            elif statusUpdate.action == "Attacking":
                color = RED
            # Update the progress worker with the test's status
            progress_worker.update(
                task_name=f"{color}{statusUpdate.action}: {statusUpdate.test_name}{RESET}",
                progress=statusUpdate.progress_position,
                total=statusUpdate.progress_total,
                breach_count=statusUpdate.status.breach_count,
                resilient_count=statusUpdate.status.resilient_count,
                error_count=statusUpdate.status.error_count,
                colour="BLUE",
            )

        # Handle invalid test results
        else:
            raise RuntimeError(
                f"BUG: Test {self.test.info['code_name']} returned an unexpected result: {result}. Please fix the test run() function!"
            )


def isResilient(test_status: TestStatus):
    """Define test as passed if there were no errors or failures during test run"""
    return test_status.breach_count == 0 and test_status.error_count == 0


def run_tests(
    client_config: ClientConfig,
    attack_config: AttackConfig,
    judge_config: Optional[JudgeConfig],
    threads_count: int,
    basic_tests_params: Optional[List[Tuple[str, dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], dict]]] = None,
    artifacts_path: Optional[str] = None,
) -> Dict[str, Dict[str, int]]:
    """
    Run the tests on the given client and attack configurations.

    Parameters
    ----------
    client_config : ClientConfig
        The configuration for the tested model.
    attack_config : AttackConfig
        The configuration for the attack.
    judge_config : JudgeConfig, optional
        The configuration for the judge.
    threads_count : int
        The number of threads to use for parallel testing.
    basic_tests_params : List[Tuple[str, dict]], optional
        A list of basic test names and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    custom_tests_params : List[Tuple[Type[TestBase], dict]], optional
        A list of custom test classes and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    artifacts_path : str, optional
        The path to the folder where artifacts (logs, reports) will be saved.

    Returns
    -------
    None
    """
    logger.debug("Initializing tests...")
    # Extract the test names from the list
    basic_test_names = [test[0] for test in basic_tests_params] if basic_tests_params else []
    logger.debug(f"List of basic tests: {basic_test_names}")

    # Print selected tests as a nicely formatted list using helper function
    if basic_test_names:
        from llamator.format_output.output_helpers import print_selected_tests

        print_selected_tests(basic_test_names, 80)

    # Instantiate all tests
    tests: List[TestBase] = instantiate_tests(
        client_config=client_config,
        attack_config=attack_config,
        judge_config=judge_config,
        basic_tests_params=basic_tests_params,
        custom_tests_params=custom_tests_params,
        artifacts_path=artifacts_path,
    )

    # Display status legend before running tests using helper function
    from llamator.format_output.output_helpers import print_status_legend

    print_status_legend(80)

    # Run tests in parallel mode
    run_tests_in_parallel(tests, threads_count)

    # Report test results
    report_results(tests)

    # Return aggregated statistics
    return _aggregate_results(tests)


def run_tests_in_parallel(tests: List[TestBase], threads_count: int = 1):
    """
    Run the tests in parallel using a thread pool.

    Parameters
    ----------
    tests : List[TestBase]
        A list of test instances to be executed.
    threads_count : int
        The number of threads to use for parallel testing.

    Returns
    -------
    None
    """
    # Create a thread pool to execute the tests in parallel
    work_pool = WorkProgressPool(threads_count)

    # Wrap the tests in TestTask objects to run them in the thread pool
    test_tasks = map(TestTask, tests)

    # Run the tests (in parallel if num_of_threads > 1)
    # A known number of tests allows for progress bar display
    work_pool.run(ThreadSafeTaskIterator(test_tasks), len(tests))


def report_results(tests: List[TestBase]):
    """
    Generate and print the test results.

    Parameters
    ----------
    tests : List[TestBase]
        A list of test instances that have been executed.

    Returns
    -------
    None
    """
    RESILIENT = f"{GREEN}✔{RESET}"
    VULNERABLE = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"

    from llamator.format_output.output_helpers import print_test_results_header

    print_test_results_header(80)

    rows = sorted(
        [
            [
                ERROR if test.status.error_count > 0 else RESILIENT if isResilient(test.status) else VULNERABLE,
                test.info["code_name"],
                test.status.breach_count,
                test.status.resilient_count,
                test.status.error_count,
                (test.status.resilient_count, test.status.total_count, isResilient(test.status)),
            ]
            for test in tests
        ],
        key=lambda x: x[1],
    )

    print_table(
        title=None,
        headers=["", "Attack Type", "Broken", "Resilient", "Errors", "Strength"],
        data=rows,
        footer_row=generate_footer_row(tests, ATTACK_TYPE_WIDTH),
        attack_type_width=ATTACK_TYPE_WIDTH,
        strength_width=STRENGTH_WIDTH,
    )
    generate_summary(tests)


def generate_footer_row(tests: List[TestBase], attack_type_width: int):
    """
    Generate the footer row for the test results table.

    Parameters
    ----------
    tests : List[TestBase]
        A list of test instances that have been executed.
    attack_type_width : int
        The maximum width for the 'Attack Type' column.

    Returns
    -------
    List
        A list representing the footer row of the results table.
    """
    RESILIENT = f"{GREEN}✔{RESET}"
    VULNERABLE = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"

    return [
        ERROR
        if all(test.status.error_count > 0 for test in tests)
        else RESILIENT
        if all(isResilient(test.status) for test in tests)
        else VULNERABLE,
        f"{'Total (# tests)' :<{attack_type_width}}",
        sum(not isResilient(test.status) for test in tests),
        sum(isResilient(test.status) for test in tests),
        sum(test.status.error_count > 0 for test in tests),
        (sum(isResilient(test.status) for test in tests), len(tests), all(isResilient(test.status) for test in tests)),
    ]


def generate_summary(tests: List[TestBase], max_line_length: Optional[int] = 80):
    """
    Generate and print a summary of the test results.

    Parameters
    ----------
    tests : List[TestBase]
        A list of test instances that have been executed.
    max_line_length : int, optional
        The maximum length of a line before wrapping, by default 80.

    Returns
    -------
    None
    """
    from llamator.format_output.output_helpers import print_summary_header

    print_summary_header(80)
    resilient_tests_count = sum(isResilient(test.status) for test in tests)

    failed_tests_list = []
    for test in tests:
        if not isResilient(test.status):
            description = " ".join(test.test_description.split())
            wrapped_description = "\n    ".join(textwrap.wrap(description, width=max_line_length))
            failed_tests_list.append(f"{test.info['code_name']}:\n    {wrapped_description}")

    failed_tests = "\n".join(failed_tests_list)
    total_tests_count = len(tests)
    resilient_tests_percentage = resilient_tests_count / total_tests_count * 100 if total_tests_count > 0 else 0

    print(
        f"Your Model passed {int(resilient_tests_percentage)}% ({resilient_tests_count} out of {total_tests_count}) of attack simulations.\n"
    )
    if resilient_tests_count < total_tests_count:
        print(f"Your Model {BRIGHT_RED}failed{RESET} the following tests:\n{RED}{failed_tests}{RESET}\n")


def setup_models_and_tests(
    attack_model: ClientBase,
    judge_model: Optional[ClientBase],
    tested_model: ClientBase,
    num_threads: Optional[int] = 1,
    basic_tests_params: Optional[List[Tuple[str, dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], dict]]] = None,
    artifacts_path: Optional[str] = None,
) -> Dict[str, Dict[str, int]]:
    """
    Set up and validate the models, then run the tests.

    Parameters
    ----------
    attack_model : ClientBase
        The model that will be used to perform the attacks.
    judge_model : ClientBase, optional
        The model that will be used to judge test results.
    tested_model : ClientBase
        The model that will be tested for vulnerabilities.
    num_threads : int, optional
        The number of threads to use for parallel testing (default is 1).
    basic_tests_params : List[Tuple[str, dict]], optional
        A list of basic test names and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    custom_tests_params : List[Tuple[Type[TestBase], dict]], optional
        A list where each element is a tuple consisting of a custom test class and a parameter dictionary
        (default is None).
    artifacts_path : str, optional
        The path to the folder where artifacts (logs, reports) will be saved.

    Returns
    -------
    Dict[str, Dict[str, int]]
        Aggregated results per attack. Empty dict if testing was not executed.
    """
    try:
        client_config = ClientConfig(tested_model)
    except (ModuleNotFoundError, ValidationError) as e:
        logger.warning(f"Error accessing the Tested Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return {}

    try:
        attack_config = AttackConfig(attack_client=ClientConfig(attack_model))
    except (ModuleNotFoundError, ValidationError) as e:
        logger.warning(f"Error accessing the Attack Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return {}

    if judge_model is not None:
        try:
            judge_config = JudgeConfig(judge_client=ClientConfig(judge_model))
        except (ModuleNotFoundError, ValidationError) as e:
            logger.warning(f"Error accessing the Judge Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
            return {}
    else:
        judge_config = None

    result_dict = run_tests(
        client_config=client_config,
        attack_config=attack_config,
        judge_config=judge_config,
        threads_count=num_threads,
        basic_tests_params=basic_tests_params,
        custom_tests_params=custom_tests_params,
        artifacts_path=artifacts_path,
    )

    return result_dict
