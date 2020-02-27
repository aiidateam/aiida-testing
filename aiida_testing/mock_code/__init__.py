# -*- coding: utf-8 -*-
"""
Defines fixtures for mocking AiiDA codes, with caching at the level of
the executable.
"""

import typing as ty

from ._fixtures import mock_code_factory

__all__: ty.Tuple[str, ...] = ('mock_code_factory', )
