import colorama
from prettytable import SINGLE_BORDER, PrettyTable

RESET = colorama.Style.RESET_ALL
BRIGHT = colorama.Style.BRIGHT
RED = colorama.Fore.RED
GREEN = colorama.Fore.GREEN
BRIGHT_YELLOW = colorama.Fore.LIGHTYELLOW_EX + colorama.Style.BRIGHT
BRIGHT_CYAN = colorama.Fore.CYAN + colorama.Style.BRIGHT


def print_table(title, headers, data, footer_row=None):
    """
    Prints a formatted table with headers, data rows, and an optional footer row.

    Parameters
    ----------
    title : str or None
        The title of the table. If None, no title will be displayed.
    headers : list
        List of header names for the table columns.
    data : list of lists
        The data to display in the table. Each inner list represents a row.
    footer_row : list, optional
        The footer row data. If provided, it will be separated from the data by a horizontal line.
    """
    # Only print the title if it's provided (not None)
    if title:
        print(f"\n{BRIGHT_CYAN}❯ {BRIGHT}{title}{RESET} ...")

    # Create the table with specified alignment and headers
    table = PrettyTable(align="l", field_names=[f"{BRIGHT}{h}{RESET}" for h in headers])
    table.set_style(SINGLE_BORDER)

    # Add each data row to the table
    for data_row in data:
        table_row = []
        for i, _ in enumerate(headers):
            table_row.append(f"{data_row[i]}")
        table.add_row(table_row)

    # Add the footer row if provided
    if footer_row:
        table.add_row(footer_row)

    # Trick below simulates a footer line separated from the header and body by a separator line
    table_lines = table.get_string().split("\n")
    if footer_row:
        # Extract the header-body separator line (second line) and put it above the last (footer) row
        table_lines = table_lines[:-2] + [table_lines[2]] + table_lines[-2:]

    # Print the table with enhanced styling
    for i, table_line in enumerate(table_lines):
        # Add color to the header row
        if i == 0:
            print(f"{BRIGHT_CYAN}{table_line}{RESET}")
        # Add color to the separator lines
        elif i == 2 or (footer_row and i == len(table_lines) - 3):
            print(f"{BRIGHT_CYAN}{table_line}{RESET}")
        # Print regular rows
        else:
            print(table_line)

    # Add some space after the table
    print()


if __name__ == "__main__":
    PASSED = f"{GREEN}✔{RESET}"
    FAILED = f"{RED}✘{RESET}"
    ERROR = f"{BRIGHT_YELLOW}⚠{RESET}"

    print_table(
        title="Test results simulated",
        headers=["", "Test", "Succesful", "Unsuccesful", "Score (1-10)"],
        data=[
            [PASSED, "Test 1 (good)", 1, 0, 10],
            [FAILED, "Test 2 (bad)", 0, 1, 0],
            [ERROR, "Test 3 (with errors)", 5, 0, 5],
        ],
    )

    print_table(
        title="Test results simulated with footer",
        headers=["", "Test", "Succesful", "Unsuccesful", "Score (1-10)"],
        data=[
            [PASSED, "Test 1 (good)", 1, 0, 10],
            [FAILED, "Test 2 (bad)", 0, 1, 0],
            [ERROR, "Test 3 (with errors)", 5, 0, 5],
        ],
        footer_row=[FAILED, "Total", 6, 1, 5.5],
    )