# -*- coding: utf-8 -*-
"""
Defines a helper for loading the ``.aiida-testing-config.yml``
configuration file.
"""

import os
import pathlib
import typing as ty

import yaml


def get_config() -> ty.Dict[str, str]:
    """
    Reads the configuration file ``.aiida-testing-config.yml``. The
    file is searched in the current working directory and all its parent
    directories.
    """
    cwd = pathlib.Path(os.getcwd())
    config: ty.Dict[str, str]
    for dir_path in [cwd, *cwd.parents]:
        config_file_path = (dir_path / '.aiida-testing-config.yml')
        if config_file_path.exists():
            with open(config_file_path) as config_file:
                config = yaml.load(config_file, Loader=yaml.SafeLoader)
                break
    else:
        config = {}
    return config
