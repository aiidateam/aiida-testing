# -*- coding: utf-8 -*-
"""A pytest plugin for mocking AiiDA codes."""

__version__ = '0.0.0a1'

from ._mock_code import mock_code_factory

__all__ = ('mock_code_factory', )
