# llamator/src/llamator/format_output/table_printing.py

from prettytable import SINGLE_BORDER, PrettyTable

from .box_drawing import strip_ansi
from .color_consts import BRIGHT, BRIGHT_CYAN, GREEN, RED, RESET

"""
Модуль для вывода результатов в виде таблицы. Используется библиотека PrettyTable.
"""


def build_progress_bar(progress, total, color, max_width):
    """
    Строит прогресс-бар с учетом максимальной ширины.
    """
    progress_str = f"{progress}/{total}"
    overhead = 3 + len(progress_str)  # 1 для '[', 1 для ']', 1 для пробела
    bar_length = max(max_width - overhead, 0)
    if total > 0:
        filled_length = int(round(bar_length * progress / float(total)))
        bar = "█" * filled_length + "-" * (bar_length - filled_length)
        return f"[{color}{bar}{RESET}] {progress_str}"
    else:
        return "[]"


def print_table(title, headers, data, footer_row=None, attack_type_width=None, strength_width=None):
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
    attack_type_width : int, optional
        The maximum width for the 'Attack Type' column.
    strength_width : int, optional
        The maximum width for the 'Strength' column.
    """
    if title:
        print(f"\n{BRIGHT_CYAN}❯ {BRIGHT}{title}{RESET} ...")

    table = PrettyTable(align="l", field_names=[f"{BRIGHT}{h}{RESET}" for h in headers])
    table.set_style(SINGLE_BORDER)

    # Устанавливаем максимальную ширину для указанных столбцов
    for field in table.field_names:
        plain_field = strip_ansi(field)
        if plain_field == "Attack Type" and attack_type_width is not None:
            table.max_width[field] = attack_type_width
        if plain_field == "Strength" and strength_width is not None:
            table.max_width[field] = strength_width

    # Добавляем строки данных
    for data_row in data:
        table_row = []
        for i, header in enumerate(headers):
            cell_value = data_row[i]
            plain_header = strip_ansi(header)
            if plain_header == "Attack Type":
                cell_str = str(cell_value)
            elif plain_header == "Strength":
                if isinstance(cell_value, tuple) and len(cell_value) == 3:
                    cell_str = build_progress_bar(
                        cell_value[0], cell_value[1], GREEN if cell_value[2] else RED, strength_width
                    )
                else:
                    cell_str = str(cell_value)
            else:
                cell_str = str(cell_value)
            table_row.append(cell_str)
        table.add_row(table_row)

    # Добавляем футер-строку, если передана
    if footer_row:
        footer_processed = []
        for i, header in enumerate(headers):
            cell_value = footer_row[i]
            plain_header = strip_ansi(header)
            if plain_header == "Attack Type":
                footer_processed.append(str(cell_value))
            elif plain_header == "Strength":
                if isinstance(cell_value, tuple) and len(cell_value) == 3:
                    footer_processed.append(
                        build_progress_bar(
                            cell_value[0], cell_value[1], GREEN if cell_value[2] else RED, strength_width
                        )
                    )
                else:
                    footer_processed.append(str(cell_value))
            else:
                footer_processed.append(str(cell_value))
        table.add_row(footer_processed)

    table_str = table.get_string().split("\n")
    if footer_row:
        # Вставляем горизонтальную черту перед футер-строкой.
        # Используем вторую строку таблицы (разделитель заголовка) как модель.
        sep_line = table_str[2]
        table_str = table_str[:-2] + [sep_line] + table_str[-2:]

    for i, line in enumerate(table_str):
        if i == 0 or i == 2:
            print(f"{BRIGHT_CYAN}{line}{RESET}")
        else:
            print(line)
    print()
