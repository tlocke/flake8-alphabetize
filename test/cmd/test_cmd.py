import os
from subprocess import CalledProcessError, run

import pytest


@pytest.mark.parametrize(
    "case,app_names",
    [
        ["blank", None],
        ["app_name", None],
    ],
)
def test_cmd_success(case, app_names):
    args = ["flake8"]

    if app_names is not None:
        args.append(f"--application-package-names {','.join(app_names)}")

    args.append(f"test/cmd/case_{case}.py")

    try:
        run(args, capture_output=True, check=True)
    except CalledProcessError as e:
        print(os.getcwd())
        print(e.returncode, e.cmd, e.output, e.stdout)
        raise e


@pytest.mark.parametrize(
    "case,app_names",
    [
        ["standard_fail", []],
        ["app_name", ["pg8000"]],
    ],
)
def test_cmd_failure(case, app_names):
    args = ["flake8"]

    if app_names is not None:
        args.append(f"--application-package-names {','.join(app_names)}")

    args.append(f"test/cmd/case_{case}.py")

    with pytest.raises(CalledProcessError):
        run(args, capture_output=True, check=True)

    # e = excinfo.value
    # print(os.getcwd())
    # print(e.returncode, e.cmd, e.output, e.stdout)
