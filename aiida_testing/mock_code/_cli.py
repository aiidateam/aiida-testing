#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Implements the executable for running a mock AiiDA code.
"""

import os
import sys
import pathlib
import shutil
import hashlib
import subprocess
import typing as ty
import fnmatch

from ._env_keys import EnvKeys

SUBMIT_FILE = '_aiidasubmit.sh'


def run() -> None:
    """
    Run the mock AiiDA code. If the corresponding result exists, it is
    simply copied over to the current working directory. Otherwise,
    the code will replace the executable in the aiidasubmit file,
    launch the "real" code, and then copy the results into the data
    directory.
    """
    # Get environment variables
    label = os.environ[EnvKeys.LABEL.value]
    data_dir = os.environ[EnvKeys.DATA_DIR.value]
    executable_path = os.environ[EnvKeys.EXECUTABLE_PATH.value]
    ignore_files = os.environ[EnvKeys.IGNORE_FILES.value].split(':')
    regenerate_data = os.environ[EnvKeys.REGENERATE_DATA.value] == 'True'

    hash_digest = get_hash().hexdigest()

    res_dir = pathlib.Path(data_dir) / f"mock-{label}-{hash_digest}"

    if regenerate_data and res_dir.exists():
        shutil.rmtree(res_dir)

    if not res_dir.exists():
        if not executable_path:
            sys.exit("No existing output, and no executable specified.")

        # replace executable path in submit file
        replace_submit_file(executable_path=executable_path)
        subprocess.call(['bash', SUBMIT_FILE])

        os.makedirs(res_dir)

        # Here we rely on getting the directory name before
        # accessing its content, hence using os.walk.
        for dirname, _, filenames in os.walk('.'):
            if dirname.startswith('./.aiida'):
                continue
            os.makedirs(os.path.join(res_dir, dirname), exist_ok=True)
            for filename in filenames:
                if any(fnmatch.fnmatch(filename, expr) for expr in ignore_files):
                    continue
                file_path = os.path.join(dirname, filename)
                res_file_path = os.path.join(res_dir, file_path)
                shutil.copyfile(file_path, res_file_path)

    else:
        # copy outputs into working directory
        for path in res_dir.iterdir():
            if path.is_dir():
                shutil.rmtree(path.name, ignore_errors=True)
                shutil.copytree(path, path.name)
            elif path.is_file():
                shutil.copyfile(path, path.name)
            else:
                sys.exit(f"Can not copy '{path.name}'.")


def get_hash() -> 'hashlib._Hash':
    """
    Get the MD5 hash for the current working directory.
    """
    md5sum = hashlib.md5()
    # Here the order needs to be consistent, thus globbing
    # with 'sorted'.
    for path in sorted(pathlib.Path('.').glob('**/*')):
        if path.is_file() and not path.match('.aiida/**'):
            with open(path, 'rb') as file_obj:
                file_content_bytes = file_obj.read()
            if path.name == SUBMIT_FILE:
                file_content_bytes = strip_submit_content(file_content_bytes)
            md5sum.update(path.name.encode())
            md5sum.update(file_content_bytes)

    return md5sum


def strip_submit_content(aiidasubmit_content_bytes: bytes) -> bytes:
    """
    Helper function to strip content which changes between
    test runs from the aiidasubmit file.
    """
    aiidasubmit_content = aiidasubmit_content_bytes.decode()
    lines: ty.Iterable[str] = aiidasubmit_content.splitlines()
    # Strip lines containing the aiida_testing.mock_code environment variables.
    lines = (line for line in lines if 'export AIIDA_MOCK' not in line)
    # Remove abspath of the aiida-mock-code, but keep cmdline
    # arguments.
    lines = (line.split("aiida-mock-code'")[-1] for line in lines)
    return '\n'.join(lines).encode()


def replace_submit_file(executable_path: str) -> None:
    """
    Replace the executable specified in the AiiDA submit file, and
    strip the AIIDA_MOCK environment variables.
    """
    with open(SUBMIT_FILE, 'r') as submit_file:
        submit_file_content = submit_file.read()

    submit_file_res_lines = []
    for line in submit_file_content.splitlines():
        if 'export AIIDA_MOCK' in line:
            continue
        if 'aiida-mock-code' in line:
            submit_file_res_lines.append(
                f"'{executable_path}' " + line.split("aiida-mock-code'")[1]
            )
        else:
            submit_file_res_lines.append(line)
    with open(SUBMIT_FILE, 'w') as submit_file:
        submit_file.write('\n'.join(submit_file_res_lines))
