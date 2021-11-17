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
def test_cmd_success(py_version, case, app_names):
    args = ["flake8"]

    if app_names is not None:
        args.append(f"--application-names {','.join(app_names)}")

    args.append(f"test/cmd/case_{case}.py")

    try:
        if py_version == (3, 6):
            run(args, check=True)
        else:
            run(args, capture_output=True, check=True)
    except CalledProcessError as e:
        print(os.getcwd())
        print(e.returncode, e.cmd, e.output, e.stdout)
        raise e


@pytest.mark.parametrize(
    "case,app_names,error",
    [
        [
            "standard_fail",
            None,
            "test/cmd/case_standard_fail.py:1:1: AZ200 Imported names are in the "
            "wrong order. Should be date, time\n",
        ],
        [
            "app_name",
            ["pg8000"],
            "test/cmd/case_app_name.py:3:1: AZ100 Import statements are in the wrong "
            "order. 'import scramp' should be before 'import pg8000'\n",
        ],
        [
            "app_name",
            ["nm3434", "pg8000", "qq9000"],
            "test/cmd/case_app_name.py:3:1: AZ100 Import statements are in the wrong "
            "order. 'import scramp' should be before 'import pg8000'\n",
        ],
    ],
)
def test_cmd_failure(py_version, case, app_names, error):
    parts = ["flake8"]

    if app_names is not None:
        parts.append(f"--application-names {','.join(app_names)}")

    parts.append(f"test/cmd/case_{case}.py")

    args = [" ".join(parts)]

    with pytest.raises(CalledProcessError) as excinfo:
        if py_version == (3, 6):
            p = run(args, check=True, shell=True, encoding="utf8")
        else:
            p = run(args, capture_output=True, check=True, shell=True, encoding="utf8")
        print(p.stdout, p.stderr)

    if py_version != (3, 6):
        e = excinfo.value
        assert e.stdout == error
        # print(os.getcwd())
        # print(e.returncode, e.cmd, e.output, e.stdout)
