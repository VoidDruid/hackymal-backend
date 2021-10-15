from typing import Any

from colorama import Fore, Style


def title(string: Any) -> str:
    return f"{Fore.BLUE}{string}{Style.RESET_ALL}"


def info(string: Any) -> str:
    return f"{Fore.GREEN}{string}{Style.RESET_ALL}"
