===============
Getting started
===============

This page should contain a short guide on what the plugin does and
a short example on how to use the plugin.

Installation
++++++++++++

Use the following commands to install ``aiida-testing``::

    pip install aiida-testing

Or, if you want to develop ``aiida-testing``::

    git clone https://github.com/aiidateam/aiida-testing
    cd aiida-testing
    pip install -e .


Usage
+++++

To use the pytest fixtures provided by ``aiida-testing`` in your tests,
you need to add the corresponding submodule to the ``pytest_plugins``
list in your ``conftest.py``. For example::

    pytest_plugins = ['aiida.manage.tests.pytest_fixtures', 'aiida_testing.mock_code', 'aiida_testing.export_cache']
