# aiida-testing

A pytest plugin to simplify testing of AiiDA plugins. This package implements two ways of running an AiiDA calculation in tests:
- `mock_code`: Implements a caching layer at the level of the executable called by an AiiDA calculation. This tests the input generation and output parsing, which is useful when testing calculation and parser plugins.
- `export_cache`: Implements an automatic export / import of the AiiDA database, to enable AiiDA - level caching in tests. This circumvents the input generation / output parsing, making it suitable for testing higher-level workflows. 
