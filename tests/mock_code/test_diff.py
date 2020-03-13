# -*- coding: utf-8 -*-
"""
Test basic usage of the mock code on examples using aiida-diff.
"""

import os
import tempfile
from aiida.engine import run_get_node
from aiida.plugins import CalculationFactory

CALC_ENTRY_POINT = 'diff'


def check_diff_output(result):
    """
    Checks the result from a diff calculation against a reference.
    """
    diff_res_lines = tuple([
        line.strip() for line in result['diff'].get_content().splitlines() if line.strip()
    ])
    assert diff_res_lines == (
        "1,2c1", "< Lorem ipsum dolor..", "<", "---",
        "> Please report to the ministry of silly walks."
    )


def test_basic(mock_code_factory, generate_diff_inputs):
    """
    Basic check of the mock code functionality.
    """
    mock_code = mock_code_factory(
        label='diff',
        data_dir_abspath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'),
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', 'file*')
    )

    res, node = run_get_node(
        CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
    )
    assert node.is_finished_ok
    check_diff_output(res)


def test_inexistent_data(mock_code_factory, generate_diff_inputs):
    """
    Check that the mock code works if there is no existing data.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        mock_code = mock_code_factory(
            label='diff',
            data_dir_abspath=temp_dir,
            entry_point=CALC_ENTRY_POINT,
            ignore_files=('_aiidasubmit.sh', 'file1.txt', 'file2.txt')
        )

        res, node = run_get_node(
            CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
        )
        assert node.is_finished_ok
        check_diff_output(res)


def test_broken_code(mock_code_factory, generate_diff_inputs):
    """
    Check that the mock code works also when no executable is given,
    when the result exists already.
    """
    mock_code = mock_code_factory(
        label='diff-broken',
        data_dir_abspath=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'),
        entry_point=CALC_ENTRY_POINT,
        ignore_files=('_aiidasubmit.sh', 'file?.txt')
    )

    res, node = run_get_node(
        CalculationFactory(CALC_ENTRY_POINT), code=mock_code, **generate_diff_inputs()
    )
    assert node.is_finished_ok
    check_diff_output(res)
