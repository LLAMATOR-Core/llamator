import colorama

RESET = colorama.Style.RESET_ALL
DIM_WHITE = colorama.Style.DIM + colorama.Fore.WHITE
LIGHT_MAGENTA = colorama.Fore.LIGHTMAGENTA_EX
MAGENTA = colorama.Fore.MAGENTA
BRIGHT = colorama.Style.BRIGHT
BRIGHT_CYAN = colorama.Fore.CYAN + colorama.Style.BRIGHT
CYAN = colorama.Fore.CYAN
BRIGHT_BLUE = colorama.Fore.BLUE + colorama.Style.BRIGHT


def print_logo() -> None:
    """
    Prints a colorful LLAMATOR logo to the console.
    """
    # Create a gradient effect for the logo
    L1 = f"{BRIGHT_CYAN}__    {CYAN}__    {BRIGHT_CYAN}___    {CYAN}__  {BRIGHT_CYAN}______  {CYAN}__________ {BRIGHT_CYAN} ____"
    L2 = f"{BRIGHT_CYAN}/ /   {CYAN}/ /   {BRIGHT_CYAN}/   |  {CYAN}/  |{BRIGHT_CYAN}/  /   |{CYAN}/_  __/ __ \\{BRIGHT_CYAN}/ __ \\"
    L3 = f"{BRIGHT_CYAN}/ /   {CYAN}/ /   {BRIGHT_CYAN}/ /| | {CYAN}/ /|{BRIGHT_CYAN}_/ / /| | {CYAN}/ / / / / {BRIGHT_CYAN}/ /_/ /"
    L4 = f"{BRIGHT_CYAN}/ /{CYAN}___/ /{BRIGHT_CYAN}___/ {CYAN}___ |/ /  / / {BRIGHT_CYAN}___ |/ / {CYAN}/ /_/ / {BRIGHT_CYAN}_, _/"
    L5 = f"{BRIGHT_CYAN}/_{CYAN}____/_{BRIGHT_CYAN}____/{CYAN}_/  |_/_/  /_/{BRIGHT_CYAN}_/  |_/_/  {CYAN}\\____/{BRIGHT_CYAN}_/ |_|"

    # Version tag
    version_line = f"{DIM_WHITE}v2.3.1{RESET}"

    # Subtitle with a different color
    subtitle = f"{BRIGHT}{LIGHT_MAGENTA}LLM Attack & Monitoring Assistant for Testing Operational Resilience{RESET}"

    # Border for the logo to make it stand out more
    top_border = f"{BRIGHT_BLUE}╔{'═' * 68}╗{RESET}"
    bottom_border = f"{BRIGHT_BLUE}╚{'═' * 68}╝{RESET}"

    # Print everything with spacing for better appearance
    print(f"\n{top_border}")
    print(f"{BRIGHT_BLUE}║{RESET}  {L1}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {L2}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {L3}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {L4}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {L5}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {' ' * 66}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {subtitle:^66}  {BRIGHT_BLUE}║{RESET}")
    print(f"{BRIGHT_BLUE}║{RESET}  {' ' * 56}{version_line:>10}  {BRIGHT_BLUE}║{RESET}")
    print(f"{bottom_border}")
    print()