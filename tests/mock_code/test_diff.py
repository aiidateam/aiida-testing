# -*- coding: utf-8 -*-
"""
Test basic usage of the mock code on examples using aiida-diff.
"""

import os
import tempfile

import pytest

from aiida import orm
from aiida.engine import run_get_node
from aiida.plugins import CalculationFactory, DataFactory

CALC_ENTRY_POINT = 'diff'


@pytest.fixture
def generate_diff_inputs(datadir):
    """
    Generates inputs for the diff calculation.
    """
    def _generate_diff_inputs():
        with open(datadir / 'file1.txt', 'rb') as f1_obj:
            file1 = orm.SinglefileData(file=f1_obj)
        with open(datadir / 'file2.txt', 'rb') as f2_obj:
            file2 = orm.SinglefileData(file=f2_obj)

        inputs = {
            "file1": file1,
            "file2": file2,
            "metadata": {
                "options": {
                    "withmpi": False,
                    "resources": {
                        "num_machines": 1,
                        "num_mpiprocs_per_machine": 1
                    }
                }
            },
            "parameters": DataFactory("diff")(dict={
                "ignore-case": False
            })
        }
        return inputs

    return _generate_diff_inputs


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


def test_basic(mock_code_factory, generate_diff_inputs):  # pylint: disable=redefined-outer-name
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


def test_inexistent_data(mock_code_factory, generate_diff_inputs):  # pylint: disable=redefined-outer-name
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


def test_broken_code(mock_code_factory, generate_diff_inputs):  # pylint: disable=redefined-outer-name
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
