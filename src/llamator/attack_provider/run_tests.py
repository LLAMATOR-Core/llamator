import textwrap
from typing import List, Tuple, Type

import colorama
from pydantic import ValidationError

from ..attack_provider.attack_registry import instantiate_tests
from ..attack_provider.work_progress_pool import ProgressWorker, ThreadSafeTaskIterator, WorkProgressPool
from ..client.attack_config import AttackConfig
from ..client.chat_client import *
from ..client.client_config import ClientConfig
from ..client.judge_config import JudgeConfig
from ..format_output.results_table import print_table
from .attack_loader import *  # noqa

# from .attack_loader import * - to register attacks defined in 'attack/*.py'
from .test_base import StatusUpdate, TestBase, TestStatus

logger = logging.getLogger(__name__)

RESET = colorama.Style.RESET_ALL
LIGHTBLUE = colorama.Fore.LIGHTBLUE_EX
BRIGHT_RED = colorama.Fore.RED + colorama.Style.BRIGHT
BRIGHT_CYAN = colorama.Fore.CYAN + colorama.Style.BRIGHT
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
BRIGHT_YELLOW = colorama.Fore.LIGHTYELLOW_EX + colorama.Style.BRIGHT

def print_box(header: str, content_lines: List[str], box_width: int) -> None:
    """
    Helper function to print a box with a header and content lines with even borders.
    """
    # Импортируем функцию для очистки ANSI последовательностей
    from ..format_output.draw_utils import strip_ansi
    # Вывод верхней границы
    print(f"{BRIGHT_CYAN}╔{'═' * box_width}╗{RESET}")
    # Расчёт отступов для заголовка с учётом ANSI последовательностей
    visible_header = strip_ansi(header)
    header_len = len(visible_header)
    left_padding = (box_width - header_len) // 2
    right_padding = box_width - header_len - left_padding
    print(f"{BRIGHT_CYAN}║{' ' * left_padding}{header}{' ' * right_padding}║{RESET}")
    # Вывод разделительной линии
    print(f"{BRIGHT_CYAN}╠{'═' * box_width}╣{RESET}")
    # Вывод строк содержимого с автоматическим выравниванием
    for line in content_lines:
        visible_line = strip_ansi(line)
        line_len = len(visible_line)
        if line_len > box_width:
            # Если строка длиннее, обрезаем её по видимой длине
            visible_line = visible_line[:box_width]
            line = visible_line
            line_len = len(visible_line)
        padding = box_width - line_len
        print(f"{BRIGHT_CYAN}║{RESET}{line}{' ' * padding}{BRIGHT_CYAN}║{RESET}")
    # Вывод нижней границы
    print(f"{BRIGHT_CYAN}╚{'═' * box_width}╝{RESET}")

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
            statusUpdate = result

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

def simpleProgressBar(progress, total, color, bar_length=50):
    """Generate printable progress bar"""
    if total > 0:
        filled_length = int(round(bar_length * progress / float(total)))
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        return f"[{color}{bar}{RESET}] {progress}/{total}"
    else:
        return "[]"

def isResilient(test_status: TestStatus):
    """Define test as passed if there were no errors or failures during test run"""
    return test_status.breach_count == 0 and test_status.error_count == 0

def run_tests(
    client_config: ClientConfig,
    attack_config: AttackConfig,
    judge_config: Optional[JudgeConfig],
    threads_count: int,
    basic_tests_params: Optional[List[Tuple[str, Dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], Dict]]] = None,
    artifacts_path: Optional[str] = None,
):
    """
    Run the tests on the given client and attack configurations.

    Parameters
    ----------
    client_config : ClientConfig
        The configuration for the tested model.
    attack_config : AttackConfig
        The configuration for the attack model.
    judge_config : JudgeConfig, optional
        The configuration for the judge model.
    threads_count : int
        The number of threads to use for parallel testing.
    basic_tests_params : List[Tuple[str, dict]], optional
        A list of basic test names and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    custom_tests_params : List[Tuple[Type[TestBase], Dict]], optional
        A list of custom test classes and parameter dictionaries (default is None).
        The dictionary keys and values will be passed as keyword arguments to the test class constructor.
    artifacts_path : str, optional
        The path to the folder where artifacts (logs, reports) will be saved.

    Returns
    -------
    None
    """
    print(f"{BRIGHT_CYAN}Running tests on your system prompt{RESET} ...")

    logger.debug("Initializing tests...")
    # Extract the test names from the list
    basic_test_names = [test[0] for test in basic_tests_params] if basic_tests_params else []
    logger.debug(f"List of basic tests: {basic_test_names}")

    # Print selected tests as a nicely formatted list using helper function
    if basic_test_names:
        content_lines = []
        for i, test_name in enumerate(basic_test_names):
            # Ensure the test name doesn't exceed the available width
            if len(test_name) > 60 - 8:
                test_name = test_name[:60 - 11] + "..."
            content_lines.append(f" {i + 1:2}. {test_name}")
        print_box("Selected Tests", content_lines, box_width=60)

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
    box_width = 60  # Consistent box width
    b_desc = f"{BRIGHT_RED}B{RESET}: Breach count - Number of successful attacks"
    r_desc = f"{GREEN}R{RESET}: Resilient count - Number of successfully blocked attacks"
    e_desc = f"{BRIGHT_YELLOW}E{RESET}: Error count - Number of errors during testing"
    legend_lines = [b_desc, r_desc, e_desc]
    print_box("Status Legend", legend_lines, box_width)

    # Run tests in parallel mode
    run_tests_in_parallel(tests, threads_count)

    # Report test results
    report_results(tests)

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

    # Print a beautiful test results header
    box_width = 84  # Width for the results box
    print(f"\n{BRIGHT_CYAN}╔{'═' * box_width}╗{RESET}")
    print(f"{BRIGHT_CYAN}║{' ' * ((box_width - 12) // 2)}TEST RESULTS{' ' * ((box_width - 12 + 1) // 2)}║{RESET}")
    print(f"{BRIGHT_CYAN}╚{'═' * box_width}╝{RESET}\n")

    # Print a table of test results
    print_table(
        title=None,  # We've already printed a more beautiful header
        headers=[
            "",
            "Attack Type",
            "Broken",
            "Resilient",
            "Errors",
            "Strength",
        ],
        data=sorted(
            [
                [
                    ERROR if test.status.error_count > 0 else RESILIENT if isResilient(test.status) else VULNERABLE,
                    f"{test.info['code_name'] + ' ':.<{50}}",
                    test.status.breach_count,
                    test.status.resilient_count,
                    test.status.error_count,
                    simpleProgressBar(
                        test.status.resilient_count,
                        test.status.total_count,
                        GREEN if isResilient(test.status) else RED,
                    ),
                ]
                for test in tests
            ],
            key=lambda x: x[1],
        ),
        footer_row=generate_footer_row(tests),
    )
    # Generate a brief summary of the results
    generate_summary(tests)

def generate_footer_row(tests: List[TestBase]):
    """
    Generate the footer row for the test results table.

    Parameters
    ----------
    tests : List[TestBase]
        A list of test instances that have been executed.

    Returns
    -------
    List
        A list representing the footer row of the results table.
    """
    RESILIENT = f"{GREEN}✔{RESET}"
    VULNERABLE = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"

    # Generate the final row for the test results table
    return [
        ERROR
        if all(test.status.error_count > 0 for test in tests)
        else RESILIENT
        if all(isResilient(test.status) for test in tests)
        else VULNERABLE,
        f"{'Total (# tests): ':.<50}",
        sum(not isResilient(test.status) for test in tests),
        sum(isResilient(test.status) for test in tests),
        sum(test.status.error_count > 0 for test in tests),
        simpleProgressBar(
            sum(isResilient(test.status) for test in tests),
            len(tests),
            GREEN if all(isResilient(test.status) for test in tests) else RED,
        ),
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
    resilient_tests_count = sum(isResilient(test.status) for test in tests)

    # Preparing descriptions with line breaks of the specified length
    failed_tests_list = []
    for test in tests:
        if not isResilient(test.status):
            description = " ".join(test.test_description.split())  # Remove extra spaces
            wrapped_description = "\n    ".join(textwrap.wrap(description, width=max_line_length))
            failed_tests_list.append(f"{test.info['code_name']}:\n    {wrapped_description}")

    failed_tests = "\n".join(failed_tests_list)

    total_tests_count = len(tests)
    resilient_tests_percentage = resilient_tests_count / total_tests_count * 100 if total_tests_count > 0 else 0

    # Print a beautiful summary header
    box_width = 84  # Same width as results box for consistency
    print(f"\n{BRIGHT_CYAN}╔{'═' * box_width}╗{RESET}")
    print(f"{BRIGHT_CYAN}║{' ' * ((box_width - 7) // 2)}SUMMARY{' ' * ((box_width - 7 + 1) // 2)}║{RESET}")
    print(f"{BRIGHT_CYAN}╚{'═' * box_width}╝{RESET}\n")

    # Displaying the percentage of successfully passed tests
    print(
        f"Your Model passed {int(resilient_tests_percentage)}% ({resilient_tests_count} out of {total_tests_count}) of attack simulations.\n"
    )

    # If there are failed tests, list them
    if resilient_tests_count < total_tests_count:
        print(f"Your Model {BRIGHT_RED}failed{RESET} the following tests:\n{RED}{failed_tests}{RESET}\n")

def setup_models_and_tests(
    attack_model: ClientBase,
    judge_model: Optional[ClientBase],
    tested_model: ClientBase,
    num_threads: Optional[int] = 1,
    basic_tests_params: Optional[List[Tuple[str, Dict]]] = None,
    custom_tests_params: Optional[List[Tuple[Type[TestBase], Dict]]] = None,
    artifacts_path: Optional[str] = None,
):
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
    custom_tests_params : List[Tuple[Type[TestBase], Dict]], optional
        A list where each element is a list consisting of a custom test class and a parameter dictionary
        (default is None).
    artifacts_path : str, optional
        The path to the folder where artifacts (logs, reports) will be saved.

    Returns
    -------
    None
    """
    # Test model setup
    try:
        client_config = ClientConfig(tested_model)
    except (ModuleNotFoundError, ValidationError) as e:
        logger.warning(f"Error accessing the Tested Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return

    # Attack model setup
    try:
        attack_config = AttackConfig(attack_client=ClientConfig(attack_model))
    except (ModuleNotFoundError, ValidationError) as e:
        logger.warning(f"Error accessing the Attack Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
        return

    # Judge model setup (если judge_model не None)
    if judge_model is not None:
        try:
            judge_config = JudgeConfig(judge_client=ClientConfig(judge_model))
        except (ModuleNotFoundError, ValidationError) as e:
            logger.warning(f"Error accessing the Judge Model: {colorama.Fore.RED}{e}{colorama.Style.RESET_ALL}")
            return
    else:
        judge_config = None

    # Run tests
    run_tests(
        client_config=client_config,
        attack_config=attack_config,
        judge_config=judge_config,
        threads_count=num_threads,
        basic_tests_params=basic_tests_params,
        custom_tests_params=custom_tests_params,
        artifacts_path=artifacts_path,
    )