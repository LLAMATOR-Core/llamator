from colorama import Style, Fore
from .draw_utils import (
    get_top_border,
    get_bottom_border,
    format_box_line,
    format_centered_line,
    get_separator_line,
    print_box_with_header,
)

BRIGHT_RED = Fore.RED + Style.BRIGHT
BRIGHT_YELLOW = Fore.LIGHTYELLOW_EX + Style.BRIGHT
BRIGHT_GREEN = Fore.GREEN + Style.BRIGHT
GREEN = Fore.GREEN
RESET = Style.RESET_ALL
BRIGHT_CYAN = Fore.CYAN + Style.BRIGHT

def print_selected_tests(selected_tests: list, box_width: int = 60) -> None:
    """
    Prints a box with a header "Selected Tests" containing a list of selected test names.
    """
    content_lines = []
    for i, test_name in enumerate(selected_tests):
        # Ensure the test name doesn't exceed the available width
        if len(test_name) > box_width - 8:
            test_name = test_name[:box_width - 11] + "..."
        content_lines.append(f" {i + 1:2}. {test_name}")
    print_box_with_header("Selected Tests", content_lines, box_width)

def print_status_legend(box_width: int = 60) -> None:
    """
    Выводит статус-легенду с корректными названиями:
    B: Broken count – число атак, нарушивших защиту.
    R: Resilient count – число успешно заблокированных атак.
    E: Errors count – число ошибок во время тестирования.
    """

    b_desc = f"{BRIGHT_RED}B:{RESET} Broken count - Number of attacks that broke system prompt protection"
    r_desc = f"{BRIGHT_GREEN}R:{RESET} Resilient count - Number of attacks that were blocked"
    e_desc = f"{BRIGHT_YELLOW}E:{RESET} Errors count - Number of errors during testing"

    legend_lines = [b_desc, r_desc, e_desc]
    print_box_with_header("Status Legend", legend_lines, box_width)

def print_testing_configuration(num_threads: int, enable_logging: bool, enable_reports: bool, report_language: str, box_width: int = 60) -> None:
    """
    Prints a box with a header "Testing Configuration" summarizing testing settings.
    """
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

def print_test_results_header(box_width: int = 84) -> None:
    """
    Prints a beautiful header for test results.
    """
    print(f"\n{BRIGHT_CYAN}╔{'═' * box_width}╗{RESET}")
    print(f"{BRIGHT_CYAN}║{' ' * ((box_width - 12) // 2)}TEST RESULTS{' ' * ((box_width - 12 + 1) // 2)}║{RESET}")
    print(f"{BRIGHT_CYAN}╚{'═' * box_width}╝{RESET}\n")

def print_summary_header(box_width: int = 84) -> None:
    """
    Prints a beautiful header for the summary section.
    """
    print(f"\n{BRIGHT_CYAN}╔{'═' * box_width}╗{RESET}")
    print(f"{BRIGHT_CYAN}║{' ' * ((box_width - 7) // 2)}SUMMARY{' ' * ((box_width - 7 + 1) // 2)}║{RESET}")
    print(f"{BRIGHT_CYAN}╚{'═' * box_width}╝{RESET}\n")