from typing import List, Union

import settings


def validate_run_level(require: Union[str, List[str]]) -> None:
    if not isinstance(require, list):
        require = [require]
    assert settings.RUN_LEVEL in require
