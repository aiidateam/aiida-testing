=======================
Using :mod:`.mock_code`
=======================

:mod:`.mock_code` provides two components:

 1. A command-line script ``aiida-mock-code`` (the *mock executable*) that is executed instead of the *actual* executable and acts as a *cache* for the outputs of the actual executable

 2. A pytest fixture :py:func:`~aiida_testing.mock_code.mock_code_factory` that sets up an AiiDA Code pointing to the mock executable

In the following, we will set up a mock code for the ``diff`` executable in three simple steps.

First, we want to define a fixture for our mocked code in the ``conftest.py``:

.. code-block:: python

    import os
    import pytest

    pytest_plugins = ['aiida.manage.tests.pytest_fixtures', 'aiida_testing.mock_code']

    # Directory where to store outputs for known inputs (usually tests/data)
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data'),

    @pytest.fixture(scope='function')
    def mocked_diff(mock_code_factory):
        """
        Create mocked "diff" code 
        """
        return mock_code_factory(
            label='diff',
            data_dir_abspath=DATA_DIR,
            entry_point='diff',
            # files *not* to copy into the data directory
            ignore_files=('_aiidasubmit.sh', 'file*')
        )
        
Second, we need to tell the mock executable where to find the *actual* ``diff`` executable by creating a ``.aiida-testing-config.yml`` file in the top level of our plugin.

.. note::
    This step is needed **only** when we want to use the actual executable to (re)generate test data.
    As long as the mock code receives data inputs whose corresponding outputs have already been stored in the data directory, the actual executable is not used.

.. code-block:: yaml

    mock_code:
      diff: /usr/bin/diff

.. note::
   Why yet another configuration file?

   The location of the actual executables will differ from one computer to the next, so hardcoding their location is not an option.
   Even the names of the executables may differ, making searching for executables in the PATH fragile.
   Finally, one could use dedicated environment variables to specify the locations of the executables, but there may be many of them, making this approach cumbersome.
   Ergo, a configuration file.

Finally, we can use our fixture in our tests as if it would provide a normal :py:class:`~aiida.orm.Code`:

.. code-block:: python

    def test_diff(mocked_diff):
        # ... set up test inputs

        inputs = {
            'code': mocked_diff,
            'parameters': parameters,
            'file1': file1,
            'file2': file2,
        }
        results, node = run_get_node( CalculationFactory('diff'), code=mocked_diff, **inputs)
        assert node.is_finished_ok

When running the test for the first time, ``aiida-mock-code`` will pipe through to the actual ``diff`` executable.
The next time, it will recognise the inputs and directly use the outputs cached in the data directory.

Don't forget to add your data directory to your test data in order to make them available in CI and to other users of your plugin!


Limitations
-----------

 * No support for remote codes yet
 * Not tested with MPI
