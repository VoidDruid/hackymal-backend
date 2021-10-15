from scripts import validate_run_level


def validate() -> None:
    validate_run_level(["prod", "dev"])
