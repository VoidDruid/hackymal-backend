import importlib
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import inquirer


AnyDict = Dict[str, Any]

BACK_CHOICE = "<Back>"
EXIT_CHOICE = "<Exit>"


def make_scripts_dict(base_dir: Path) -> AnyDict:
    scripts_dict = {}
    for dirname, _, files in os.walk(base_dir):
        scripts = list(
            filter(
                lambda filename: (
                    not filename.startswith("__")
                    and (filename.endswith(".py") or filename.endswith(".sh"))
                ),
                files,
            )
        )
        if scripts:
            scripts_dict[dirname] = scripts
    return scripts_dict


def choose_dir(scripts_dict: AnyDict, base_dir: Path) -> str:
    choices = list(
        map(lambda directory: directory[len(str(base_dir)) + 1 :], scripts_dict.keys())
    )[1:]
    choices.append(EXIT_CHOICE)

    prompt = "Type"
    questions = [
        inquirer.List(
            prompt,
            message="Choose type",
            choices=choices,
        ),
    ]
    return inquirer.prompt(questions)[prompt]


def choose_script(scripts: List[str]) -> str:
    prompt = "Script"
    scripts.append(BACK_CHOICE)
    questions = [
        inquirer.List(
            prompt,
            message="Choose script",
            choices=scripts,
        ),
    ]
    return inquirer.prompt(questions)[prompt]


def run_script(path_to_script: Path) -> None:
    with open(str(path_to_script), "r") as script_file:
        executable = script_file.readline().startswith("#!")

    script = str(path_to_script.relative_to(Path(sys.argv[0]).parent))
    executor = "python" if script.endswith("py") else "bash"
    base_package_path, script_module_path = script.split("/")
    script_module_path = script_module_path.replace(".py", "")

    terminal_width = shutil.get_terminal_size((80, 20))[0]

    print("Running script: ", script)
    print()
    print("-" * terminal_width)
    print(
        " " * ((terminal_width - len(script_module_path)) // 2)
        + script_module_path.upper()
    )

    if executable:
        try:
            subprocess.call(script)
        except PermissionError:
            os.chmod(script, os.stat(script).st_mode | stat.S_IEXEC)
            subprocess.call(script)
    else:
        if executor == "python":
            base_package = importlib.import_module(base_package_path)
            base_package.validate()  # type:ignore

            script_module = importlib.import_module(
                f"{base_package_path}.{script_module_path}"
            )
            script_module.main()  # type:ignore
        else:
            subprocess.call(["bash", script])


def get_script(base_dir: Path) -> Path:
    script_ = None

    while script_ is None or script_ == BACK_CHOICE:
        scripts_dict = make_scripts_dict(base_dir)

        dir_ = choose_dir(scripts_dict, base_dir)
        if dir_ == EXIT_CHOICE:
            sys.exit(0)
        directory = base_dir / dir_

        script_ = choose_script(scripts_dict[str(directory)])

    script = directory / script_
    return script


@click.command()
@click.argument(
    "script",
    nargs=1,
    required=False,
)
def run(script: Optional[str] = None) -> None:
    """Run service scripts easily"""
    base_dir = Path(sys.argv[0]).parent
    sys.path.append(str(base_dir))
    if script:
        to_run = base_dir / script
    else:
        to_run = get_script(base_dir)
    run_script(to_run)


if __name__ == "__main__":
    run()
